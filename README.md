# 🤖 Rusty – Your Personal Voice AI Assistant

Rusty is a locally running voice-based AI assistant that listens to your commands, understands your intent, and takes action — like opening apps, playing music, or holding a conversation with Gemini. Now evolving to support **neurodivergent-friendly** features, especially those that help with **ADHD-focused productivity**.

---

## 🚀 Features

* 🎙️ Voice command recognition using [OpenAI Whisper](https://github.com/openai/whisper)
* 🧠 Smart conversations using Google Gemini (Generative AI)
* 🎵 Spotify integration (play/pause/liked songs)
* 📁 App control (open apps like Chrome, Discord, etc.)
* 🧠 Learns your personal command styles over time
* 🔒 Runs completely on your device (no cloud audio)
* 🧠 Experimental ADHD-aware focus assistant features

---

📍 Features Roadmap
Rusty is a voice-activated desktop assistant designed to help you interact with your system and AI models in a natural and productive way. Below is the current and planned roadmap for its features.

### ✅ Core Features (Completed)

* 🎙️ **Voice Activation & Wake Word**
  Responds to a custom wake word ("Hey bro", etc.) using Whisper and speech recognition.

* 🧠 **Conversational AI (Gemini)**
  Integrates Google’s Gemini API for contextual, chat-style conversations.

* 🗂️ **Intent Detection & Routing**
  Classifies user commands (e.g., "play music", "open Discord") and routes to appropriate functions.

* 📂 **App Launcher Module**
  Opens apps like Chrome, Spotify, Discord, etc., based on voice commands.

* 🎵 **Spotify Integration**
  Play, pause, skip, or like Spotify songs using voice.

* 💾 **Memory Module**
  Learns and recalls user-specific data using "remember" and "recall" style commands.

* 🧠 **Style Learning (Personalized Input Parser)**
  Learns your phrasing style and maps "when I say X" → "do Y" with persistent mappings.

* 🔒 **Environment Config Management**
  Securely loads API keys and settings from .env via a config module.

---

### 🧪 In Progress / Experimental

* 🧬 **Conversation History Memory**
  Let Rusty maintain session-based or persistent conversation memory using vector stores or Redis.

* 🗣️ **Personality Tuning**
  Customize Rusty’s tone/personality (e.g., sarcastic, formal, chill).

* 🧱 **Modular Plugin System**
  Allow external Python scripts or user-added actions to plug into Rusty.

* 📖 **Context-Aware Learning**
  Let Rusty learn from your past interactions to better handle future ones.

---

### 🧠 ADHD-Focused Features (WIP/Planned)

* 🧩 **Focus Mode with Voice Nudges**
  Activate Pomodoro-style sessions with voice reminders and “blank brain” mode to reduce overwhelm.

* 🧠 **Task Recall Assistant**
  Rusty will remember your dropped/incomplete tasks and gently bring them up later.

* 🧘 **Voice-Based Anchoring**
  Let Rusty talk you through grounding or calming exercises if you're overstimulated.

* 🧵 **Threaded Thought Reminder**
  If you say “Remind me later”, Rusty will follow up based on your energy or time.

* 🧑‍🎨 **Personalized Voice Reinforcement**
  Rusty adapts tone and phrasing to how *you* respond best: chill, affirming, playful, or structured.

* 🧠 **Neurodivergent Mode Toggle**
  A toggle that adjusts task delivery pace, voice tone, and repetition tolerance based on ADHD-friendly presets.

---

### 🧭 Planned Features (Upcoming)

* 🪟 **Minimal GUI Overlay**
  A floating mic icon or window showing conversation transcripts and quick toggles.

* 🎯 **Goal/Task Assistant**
  Set reminders, timers, daily check-ins, or to-do tasks via voice.

* 🧩 **Hybrid Model Support**
  Seamless fallback between Gemini API and local LLMs (like TinyLLaMA via llama-cpp-python).

* 📦 **Rusty Packager**
  Export Rusty as a background .exe (for Windows) or bundled app for easy use.

* 🛜 **Local Server API (Rusty API)**
  Let other programs talk to Rusty over HTTP for command automation or integration.

---

## 🛠️ Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

### SETUP

1. Create a `.env` file in the root folder:

```
GEMINI_API_KEY=your_google_api_key
SPOTIFY_CLIENT_ID=your_spotify_id
SPOTIFY_CLIENT_SECRET=your_spotify_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
WAKE_WORD=hey bro
```

2. RUN RUSTY:

```bash
run_rusty.bat
```

---

## 📁 Project Structure

```
rusty_core/
├── main.py
├── voice.py
├── intent_router.py
├── config.py
├── gpt_conversation.py
├── style_learning.py
├── memory.py
├── ...
```

---

## 📄 License

MIT (or insert license here)

---

Want to contribute? PRs and feedback welcome!
