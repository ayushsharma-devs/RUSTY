from google.generativeai import GenerativeModel

gemini = GenerativeModel("gemini-1.5-flash")

def detect_intent_gemini(user_input):
    prompt = f"""
You are an intent detector for a personal assistant named Rusty.

Choose the correct intent based on the user's message.

Respond ONLY with the intent name in snake_case. Do NOT explain.

### Intent List:
- capability_list
- capability_demo
- play_music
- play_playlist
- play_liked
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
-whats_playing
- open_app
- close_app
- remember_fact
- recall_fact
- list_memory
- clear_memory
- teach_command
- chat
- set_volume
- battery 
- mute
- unmute
- screenshot
- lock
- shutdown
- sleep
- restart

### Examples:
Input: "what can you do"  
Intent: capability_list


Input: "play lofi beats"  
Intent: play_music

Input: "start my workout playlist"  
Intent: play_playlist

Input: "pause the song"  
Intent: pause_music

Input: "open discord"  
Intent: open_app

Input: "remember that my birthday is November 15"  
Intent: remember_fact

Input: "what do you remember about my birthday"  
Intent: recall_fact

Input: "what is 25 x 4?"  
Intent: chat

Input: "tell me a joke"  
Intent: chat

### Now classify this:
Input: "{user_input}"  
Intent:
"""

    try:
        response = gemini.generate_content(prompt)
        intent = response.text.strip().lower()
        intent = intent.replace("intent:", "").strip().split()[0]

        return intent
    except Exception as e:
        print("Gemini intent error:", e)
        return "chat"
