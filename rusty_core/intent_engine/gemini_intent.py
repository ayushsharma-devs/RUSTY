from intent_engine.intent_map import intent_keywords
from google.generativeai import GenerativeModel

gemini = GenerativeModel("gemini-1.5-flash")

def detect_intent_gemini(user_input):
  
    prompt = f"""
You are an intent detector for a personal assistant named Rusty.  
Choose one of the following intents **based on the user's message**.  

Respond with **only the intent name** in snake_case.

### Intent List:
- play_music
- play_playlist
- play_album
- play_artist
- pause_music
- resume_music
- next_music
- prev_song
- volume_up
- volume_down
- set_volume
- mute
- shuffle
- open_app
- close_app
- remember_fact
- recall_fact
- list_memory
- clear_memory
- teach_command
- chat

### Notes:
- If the message is **general conversation**, jokes, questions, or math → use `chat`
- Only use `recall_fact` if the user is asking about something **they previously told me**
- If uncertain, default to `chat`

Input: "what is 25 times 40"  
Intent:

"""

    try:
        response = gemini.generate_content(prompt)
        intent = response.text.strip().split()[0].lower()
        return intent
    except Exception as e:
        print("Gemini intent error:", e)
        return "chat"
