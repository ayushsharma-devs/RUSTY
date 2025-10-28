from google.generativeai import GenerativeModel
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import GEMINI_INTENT_MODEL

gemini = GenerativeModel(GEMINI_INTENT_MODEL)

def detect_intent_gemini(user_input):
    prompt = f"""
You are an intent detector for a personal assistant named Rusty.

Analyze the user's message and return TWO things:
1. The intent (what they want to do)
2. Context keywords needed from memory (if any)

Respond ONLY in this JSON format:
{{"intent": "intent_name", "context_needed": ["keyword1", "keyword2"]}}

If NO memory context is needed, use an empty array: {{"intent": "intent_name", "context_needed": []}}

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
- whats_playing
- open_app
- close_app
- remember_fact
- recall_fact
- list_memory
- clear_memory
- teach_command
- chat
- battery 
- unmute
- screenshot
- lock
- shutdown
- sleep
- restart

### Context Keywords (use when user might need personal info):
Use context_needed when the user asks about:
- Their personal info: birthday, name, age, address, location, city, job, school
- Their preferences: favorite color, food, etc.
- Their belongings: pet names, car, etc.

### Examples:

Input: "what can you do"  
Output: {{"intent": "capability_list", "context_needed": []}}

Input: "play lofi beats"  
Output: {{"intent": "play_music", "context_needed": []}}

Input: "remember that my birthday is November 15"  
Output: {{"intent": "remember_fact", "context_needed": []}}

Input: "what's my address?"
Output: {{"intent": "chat", "context_needed": ["address", "location"]}}

Input: "when is my birthday?"
Output: {{"intent": "chat", "context_needed": ["birthday"]}}

Input: "what's the weather?"
Output: {{"intent": "chat", "context_needed": ["address", "location", "city"]}}

Input: "tell me a joke"
Output: {{"intent": "chat", "context_needed": []}}

### Now classify this:
Input: "{user_input}"  
Output (JSON only):"""

    try:
        response = gemini.generate_content(prompt)
        result = response.text.strip()
        
        # Clean up the response to extract JSON
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        
        import json as json_module
        data = json_module.loads(result)
        
        return {
            "intent": data.get("intent", "chat").lower().strip(),
            "context_needed": data.get("context_needed", [])
        }
        
    except Exception as e:
        print(f"Gemini intent error: {e}")
        return {"intent": "chat", "context_needed": []}
