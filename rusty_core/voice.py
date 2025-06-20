import subprocess
import tempfile
import threading
import queue
import time
import string
import os

import numpy as np
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
import edge_tts
import noisereduce as nr
import librosa

# --- TTS Setup with Edge-TTS ---
tts_queue = queue.Queue()
speaking_event = threading.Event()

async def speak_async(text):
    if not text.strip():
        return
    try:
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
        output_path = "tts_output.mp3"
        await communicate.save(output_path)

        subprocess.run([
            "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", output_path
        ])
    except Exception as e:
        print(f"❌ EdgeTTS error: {e}")

def tts_worker():
    import asyncio
    while True:
        text = tts_queue.get()
        if text is None:
            break
        speaking_event.set()
        print(f"[🔊 speak()] Speaking: {text} | Queue size: {tts_queue.qsize()}", flush=True)
        asyncio.run(speak_async(text))
        speaking_event.clear()
        tts_queue.task_done()

# Start TTS thread
tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()

def speak(text):
    if text and isinstance(text, str) and text.strip():
        tts_queue.put(text)

# --- Faster-Whisper Setup ---
model = WhisperModel("medium.en", device="cpu", compute_type="int8")

# --- Recording ---
def record_audio(duration=5, sample_rate=16000):
    try:
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
        return np.squeeze(audio), sample_rate
    except Exception as e:
        print(f"❌ [record_audio] Error: {e}")
        return np.zeros(sample_rate * duration, dtype='int16'), sample_rate

# --- Transcription ---
def transcribe(audio, sample_rate):
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            sf.write(temp_wav.name, audio, sample_rate)
            sf.write("last_input.wav", audio, sample_rate)  # Debug copy
            temp_wav.flush()
            segments, info = model.transcribe(
                temp_wav.name,
                language="en",
                beam_size=10,
                vad_filter=True,
                vad_parameters={"threshold": 0.5}
            )
            text = " ".join([segment.text for segment in segments]).strip().lower()
            text = text.translate(str.maketrans('', '', string.punctuation))
            print(f"🧠 Whisper heard: '{text}'")
        os.remove(temp_wav.name)
        return text
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return ""

# --- Listening ---
def adaptive_record(max_duration=5, silence_buffer=10, silence_duration=2.0, sample_rate=16000):
    chunk_duration = 0.1
    chunk_size = int(sample_rate * chunk_duration)
    max_chunks = int(max_duration / chunk_duration)
    silence_chunks_needed = int(silence_duration / chunk_duration)

    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
            silent_data, _ = stream.read(int(sample_rate * 0.5))
            bg_rms = np.sqrt(np.mean(silent_data.astype(np.float32)**2))
            silence_threshold = max(bg_rms + silence_buffer, 20)

        print(f"🔈 Silence threshold set to: {silence_threshold:.2f}")
        audio_chunks = []
        silence_counter = 0

        with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
            for _ in range(max_chunks):
                chunk, _ = stream.read(chunk_size)
                audio_chunks.append(chunk)

                rms = np.sqrt(np.mean(chunk.astype(np.float32)**2))
                print(f"🟡 RMS: {rms:.2f} | Threshold: {silence_threshold:.2f} | Silence Counter: {silence_counter}")

                if rms < silence_threshold:
                    silence_counter += 1
                else:
                    silence_counter = 0

                if silence_counter >= silence_chunks_needed:
                    print("🔇 Detected consistent silence, stopping early.")
                    break

        full_audio = np.concatenate(audio_chunks, axis=0).astype(np.float32)
        if len(full_audio.shape) > 1:
            full_audio = np.mean(full_audio, axis=1)
        full_audio = librosa.resample(full_audio, orig_sr=sample_rate, target_sr=16000)

        try:
            reduced_audio = nr.reduce_noise(y=full_audio, sr=16000)
            return reduced_audio.astype(np.int16), 16000
        except Exception as e:
            print(f"⚠️ Noise reduction failed: {e}")
            return full_audio.astype(np.int16), 16000

    except Exception as e:
        print(f"❌ [adaptive_record] Error: {e}")
        return np.zeros(sample_rate * max_duration, dtype='int16'), sample_rate

def listen(max_attempts=3):
    attempt = 0
    while attempt < max_attempts:
        try:
            print("🎤 Listening...")
            while speaking_event.is_set():
                time.sleep(0.1)

            audio, sr = adaptive_record()
            text = transcribe(audio, sr).strip().lower()
            print(f"🎙️ You probably said: '{text}'")

            if (
                len(text) < 2 or
                text in ["uh", "um", "hmm", ""] or
                not any(c.isalpha() for c in text) or
                len(text.split()) < 2 or
                all(w == text.split()[0] for w in text.split())
            ):
                print(f"❓ Unclear input: '{text}' → Retrying...")
                speak("Could you repeat that?")
                attempt += 1
                continue

            return text

        except Exception as e:
            print(f"❌ Listen error: {e}")
            return "timeout"

    print("⚠️ Too many unclear attempts.")
    speak("Sorry, I didn't catch that.")
    return "timeout"
