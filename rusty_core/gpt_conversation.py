# gpt_conversation.py

import google.generativeai as genai
from config import GEMINI_API_KEY
from memory import add_to_memory, get_memory

# Configure API
genai.configure(api_key=GEMINI_API_KEY)

# Load model
model = genai.GenerativeModel("gemini-1.5-flash")

# Create chat object (with memory context restored)
chat = model.start_chat(history=[])

def generate_response(user_input):
    try:
        add_to_memory("user", user_input)

        # Inject Rusty personality into prompt
        personality = (
        "You are Rusty, a chill, sarcastic, funny, but helpful assistant. "
        "Always answer like a close friend who's good with tech. Keep it short, natural, and avoid sounding robotic."
        )

        response = chat.send_message(f"{personality}\n\nUser: {user_input}")
        reply = response.text.strip()
        add_to_memory("assistant", reply)

        # Passive memory capture
        import re
        from memory import remember

        match = re.search(r"my (.+?) is (.+)", user_input.lower())
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            print(f"🧠 Auto-storing: {key} = {value}")
            remember(key, value)

        return reply

    except Exception as e:
        print("Gemini API error:", e)
        return "Rusty had a hiccup. Try again in a moment."
