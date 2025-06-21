import os
import time
import threading

import queue
import numpy as np
import sounddevice as sd
import webrtcvad
import collections
from faster_whisper import WhisperModel
import edge_tts
from tempfile import NamedTemporaryFile
import tempfile
import subprocess

# --- Config ---
SAMPLE_RATE = 16000
FRAME_DURATION = 30  # ms
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)  # 480 samples
MAX_SILENCE_DURATION = 1.0  # seconds
VOICE = os.getenv("TTS_VOICE", "en-US-GuyNeural")

# --- State Flags ---
speaking_event = threading.Event()
stop_event = threading.Event()

# --- TTS Queue ---
tts_queue = queue.Queue()

# --- Whisper Model ---
whisper_model = WhisperModel("medium.en", device="cpu", compute_type="int8")

# --- Audio Frame Buffer ---
class AudioBuffer:
    def __init__(self, max_seconds=10):
        self.max_frames = int(SAMPLE_RATE / FRAME_SIZE * max_seconds)
        self.frames = collections.deque(maxlen=self.max_frames)

    def add_frame(self, frame):
        self.frames.append(frame)

    def get_audio(self):
        return b"".join(self.frames)

# --- WebRTC VAD ---
vad = webrtcvad.Vad()
vad.set_mode(2)  # 0-3 (3 is most aggressive)

# --- TTS Function ---
async def speak_async(text):
    if not text.strip():
        return
    try:
        # Create a temporary mp3 file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tmp_path = tmpfile.name

        # Save TTS output to the temp file
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
        await communicate.save(tmp_path)

        # Play the audio
        try:
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", tmp_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"🎧 ffplay playback failed: {e}")

        # Delete the temp file after playback
        os.remove(tmp_path)

    except Exception as e:
        print(f"❌ TTS Error: {e}")
# --- TTS Worker ---
def tts_worker():
    import asyncio
    while True:
        try:
            text = tts_queue.get()
            if text is None:
                break

            speaking_event.set()
            print(f"[🔊 speak()] Speaking: {text} | Queue size: {tts_queue.qsize()}", flush=True)

            try:
                asyncio.run(speak_async(text))
            except Exception as e:
                print(f"❌ TTS async error: {e}")
            finally:
                print("🟢 speak_async finished or failed, clearing event")
                speaking_event.clear()

        except Exception as e:
            print(f"❌ tts_worker thread error: {e}")
        finally:
            tts_queue.task_done()


# --- Speak Wrapper ---
def speak(text):
    if isinstance(text, str) and text.strip():
        tts_queue.put(text)

# --- Listen Function ---
def listen():
    print("🎤 Starting listen()")
    ring_buffer = collections.deque(maxlen=30)
    triggered = False
    voiced_frames = []
    audio_buffer = AudioBuffer()

    print("🔊 Opening audio stream...")
    stream = sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=FRAME_SIZE,
                                dtype='int16', channels=1)
    with stream:
        print("🎙️ Stream opened.")
        while not stop_event.is_set():
            if speaking_event.is_set():
                print("⏳ Waiting for TTS to finish...")
                time.sleep(0.1)
                continue

            frame, _ = stream.read(FRAME_SIZE)
            print("📦 Frame read")

            is_speech = vad.is_speech(frame, SAMPLE_RATE)
            print(f"🧪 Speech detected: {is_speech}")

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                maxlen = ring_buffer.maxlen or 1
                print(f"🟢 Voiced frames: {num_voiced}/{maxlen}")
                if num_voiced > 0.9 * maxlen:
                    print("✅ Triggered by speech")
                    triggered = True
                    for f, _ in ring_buffer:
                        voiced_frames.append(f)
                    ring_buffer.clear()
            else:
                voiced_frames.append(frame)
                audio_buffer.add_frame(frame)
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                print(f"🔕 Unvoiced frames: {num_unvoiced}")
                if num_unvoiced > MAX_SILENCE_DURATION * 1000 / FRAME_DURATION:
                    print("🛑 Silence threshold hit. Breaking.")
                    break

    print("💾 Converting to np array")
    audio_data = np.frombuffer(audio_buffer.get_audio(), dtype=np.int16)
    if len(audio_data) < 1000:
        print("📉 Final audio too short, forcing retry.")
        return "timeout"

    print("🎧 Writing temp WAV for Whisper")
    with NamedTemporaryFile(suffix=".wav", delete=False) as f:
        import soundfile as sf
        sf.write(f.name, audio_data, SAMPLE_RATE)
        print("🧠 Transcribing with Whisper...")
        segments, _ = whisper_model.transcribe(f.name, language="en", beam_size=5)
        text = " ".join([seg.text for seg in segments]).strip().lower()
        print(f"🧠 Whisper heard: '{text}'")
        os.remove(f.name)

    return text if text else "timeout"

# --- Init & Stop ---
def init_voice_engine():
    threading.Thread(target=tts_worker, daemon=True).start()

def stop_listening():
    stop_event.set()
    tts_queue.put(None)

# --- End ---
