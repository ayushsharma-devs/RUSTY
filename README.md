# 🤖 Rusty – Your Personal Voice AI Assistant

Rusty is a locally running voice-based AI assistant that listens to your commands, understands your intent, and takes action — like opening apps, playing music, or holding a conversation with Gemini.

---

## 🚀 Features

- 🎙️ Voice command recognition using [OpenAI Whisper](https://github.com/openai/whisper)
- 🧠 Smart conversations using Google Gemini (Generative AI)
- 🎵 Spotify integration (play/pause/liked songs)
- 📁 App control (open apps like Chrome, Discord, etc.)
- 🧠 Learns your personal command styles over time
- 🔒 Runs completely on your device (no cloud audio)

---

## 🛠️ Requirements

Install dependencies with:

```bash
pip install -r requirements.txt

SETUP
1. Create a .env file in the root folder:
GEMINI_API_KEY=your_google_api_key
SPOTIFY_CLIENT_ID=your_spotify_id
SPOTIFY_CLIENT_SECRET=your_spotify_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
WAKE_WORD=hey bro

2. RUN RUSTY
python -m rusty_core.main


PROJECT STRUCTURE
rusty_core/
├── main.py
├── voice.py
├── intent_router.py
├── config.py
├── gpt_conversation.py
├── style_learning.py
├── memory.py
├── ...


LICENSE

---

### 💾 Step 3: Save the file

Then you’re ready to push it.

---

Let me know when you’re done pasting — I’ll help with the next `git add`, `commit`, and `push` commands.

