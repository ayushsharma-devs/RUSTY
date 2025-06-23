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
import asyncio
import subprocess
import soundfile as sf

# --- Config ---
SAMPLE_RATE = 16000
FRAME_DURATION = 30  # ms
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)
MAX_SILENCE_DURATION = 0.5  # seconds
VOICE = os.getenv("TTS_VOICE", "en-US-GuyNeural")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

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
vad.set_mode(3)

# --- TTS Async ---
async def speak_async(text):
    if not text.strip():
        return
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tmp_path = tmpfile.name

        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(tmp_path)

        process = await asyncio.create_subprocess_exec(
            "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", tmp_path,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await process.wait()

        os.remove(tmp_path)

    except Exception as e:
        print(f"❌ TTS Error: {e}")

# --- TTS Worker ---
def tts_worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def process_queue():
        while True:
            text = await loop.run_in_executor(None, tts_queue.get)
            if text is None:
                print("🛑 TTS worker shutting down.")
                tts_queue.task_done()
                break

            speaking_event.set()
            print(f"[🔊 speak()] Speaking: {text}", flush=True)

            try:
                await speak_async(text)
            except Exception as e:
                print(f"❌ TTS async error: {e}")
            finally:
                speaking_event.clear()
                tts_queue.task_done()

    try:
        loop.run_until_complete(process_queue())
    finally:
        loop.close()

# --- Speak Wrapper ---
def speak(text):
    if isinstance(text, str) and text.strip():
        tts_queue.put(text)

# --- Listen Function ---
def listen(): 
    print("🎤 Listening...")
    ring_buffer = collections.deque(maxlen=30)
    assert ring_buffer.maxlen is not None  # silence Pyright
    pre_trigger_buffer = collections.deque(maxlen=int(1.0 * 1000 / FRAME_DURATION))  # ~1 sec pre-buffer
    triggered = False
    voiced_frames = []
    audio_buffer = AudioBuffer()

    stream = sd.InputStream(samplerate=SAMPLE_RATE, blocksize=FRAME_SIZE,
                                dtype='int16', channels=1)
    with stream:
        while not stop_event.is_set():
            if speaking_event.is_set():
             
                time.sleep(0.1)
                continue

            frame, _ = stream.read(FRAME_SIZE)
            
            pre_trigger_buffer.append(frame)

            is_speech = vad.is_speech(frame, SAMPLE_RATE)
           
            if not triggered:
                ring_buffer.append((frame, is_speech))
                
                num_voiced = len([f for f, speech in ring_buffer if speech])
              
                if num_voiced > 0.9 * ring_buffer.maxlen:
                    triggered = True

                    # 🔁 Include pre-trigger audio
                    for f in pre_trigger_buffer:
                        voiced_frames.append(f)
                        audio_buffer.add_frame(f)

                    # 🔁 Include ring buffer frames
                    for f, _ in ring_buffer:
                        voiced_frames.append(f)
                        audio_buffer.add_frame(f)

                    ring_buffer.clear()
            else:
                voiced_frames.append(frame)
                audio_buffer.add_frame(frame)
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > MAX_SILENCE_DURATION * 1000 / FRAME_DURATION:
                    break

    audio_data = np.frombuffer(audio_buffer.get_audio(), dtype=np.int16)
    if len(audio_data) < 1000:
        return "timeout"

    # 🔊 Save captured audio for debugging

    try:
        segments, _ = whisper_model.transcribe(audio=audio_data, language="en")
        text = " ".join([seg.text for seg in segments]).strip().lower()
    except Exception as e:
        print(f"❌ Whisper error: {e}")
        return "timeout"

    return text if text else "timeout"

# --- Init & Stop ---
def init_voice_engine():
    threading.Thread(target=tts_worker, daemon=True).start()

def stop_listening():
    stop_event.set()
    tts_queue.put(None)
