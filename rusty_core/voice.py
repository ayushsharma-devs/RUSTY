import whisper
import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile as wav
import pyttsx3
import string
# Initialize text-to-speech engine
engine = pyttsx3.init()

# Load Whisper model once (upgrade from 'base' to 'medium' or 'large' for better accuracy)
model = whisper.load_model("small")  # change to "large" if your system can handle it

# Global transcription options
TRANSCRIBE_OPTS = {
    "fp16": False,
    "language": "en",
    "temperature": 0.2,
    "initial_prompt": (
        "This is a conversation with an English-speaking desktop voice assistant named Rusty. "
        "Rusty helps open apps like Spotify, Chrome, and Discord, and answers general questions."
    )
}

def speak(text):
    print(f"🗣️ Rusty: {text}")
    engine.say(text)
    engine.runAndWait()

def record_audio(duration=5, sample_rate=16000, silent=False):
    if not silent:
        print("🎙️ Listening...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    return audio_data, sample_rate
def transcribe(audio_data, sample_rate):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav.write(f.name, sample_rate, audio_data)
        path = f.name
    result = model.transcribe(
        path,
        fp16=False,
        language="en",
        temperature=0.2,
        initial_prompt="This is a conversation with an English-speaking AI assistant named Rusty."
    )

    if not result or "text" not in result or not result["text"].strip():
        print("❓ No transcription result.")
        return ""

    text = result["text"].strip().lower()

    text = text.translate(str.maketrans('', '', string.punctuation))  # 🧹 remove all punctuation
    print(f"🧠 You said: {text}")
    return text


def listen(duration=5):
    try:
        audio_data, sample_rate = record_audio(duration=duration)
        text = transcribe(audio_data, sample_rate)

        if len(text) < 2 or text in ["uh", "um", "hmm", ""] or not any(c.isalpha() for c in text):
            print("❓ No clear input detected.")
            return "timeout"

        return text
    except Exception as e:
        print(f"❌ Error: {e}")
        return "timeout"

def listen_for_wake_word(wake_word="hey bro"):
    speak("🎧 Waiting for wake word...")
    # Skip noisy startup audio
    for _ in range(2):
        try:
            record_audio(duration=3, silent=True)
        except:
            pass


    while True:
        try:
            audio_data, sample_rate = record_audio(duration=3)
            text = transcribe(audio_data, sample_rate)

            if not text:
                continue  # skip if nothing was transcribed

            if wake_word in text:
                speak("Yes?")
                return True

        except Exception as e:
            print(f"⚠️ Wake word error: {e}")
