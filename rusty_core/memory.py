import json
import os
import re
from collections import deque
from difflib import get_close_matches

# Files
MEMORY_FILE = "rusty_core/rusty_memory.json"
CONTEXT_FILE = "rusty_core/rusty_context.json"

# Short-term memory buffer
memory_buffer = deque(maxlen=20)

# ---------- Short-Term Memory ----------

def add_to_memory(role, content):
    memory_buffer.append({"role": role, "parts": [content]})

def get_memory():
    return list(memory_buffer)

def clear_memory():
    memory_buffer.clear()

def save_memory_context():
    with open(CONTEXT_FILE, "w") as f:
        json.dump(list(memory_buffer), f, indent=2)

def load_memory_context():
    global memory_buffer
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "r") as f:
            data = json.load(f)
            memory_buffer = deque(data, maxlen=20)

def recent_mention(topic):
    """Returns the most recent thing user said about <topic> from short-term memory"""
    topic = topic.lower()
    for msg in reversed(memory_buffer):
        if msg["role"] == "user" and topic in msg["parts"][0].lower():
            return msg["parts"][0]
    return None

# ---------- Long-Term Memory ----------

def remember(key, value):
    memory = {}
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    memory[key.lower()] = value
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)
    return f"🧠 Got it. I’ll remember that {key} is {value}."
 # recent context buffer

MEMORY_FILE = "rusty_core/data/long_term_memory.json"

REPHRASE_TEMPLATES = {
    "name": "Your name is {}.",
    "birthday": "Your birthday is {}.",
    "city": "You said you live in {}.",
    "location": "You're in {}.",
    "dog": "Your dog's name is {}.",
    "cat": "Your cat's name is {}.",
}

def rephrase(key, value):
    for trigger, template in REPHRASE_TEMPLATES.items():
        if trigger in key:
            return template.format(value.capitalize())
    return f"You told me that {key} is {value}."

def recall(user_input):
    user_input = user_input.lower().strip()
    user_input = re.sub(r"[^\w\s]", "", user_input)

    # -------- LONG-TERM STRUCTURED MEMORY --------
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)

        # 1. Exact match
        if user_input in memory:
            return rephrase(user_input, memory[user_input])

        # 2. Fuzzy key match
        close_keys = get_close_matches(user_input, memory.keys(), n=1, cutoff=0.6)
        if close_keys:
            key = close_keys[0]
            return rephrase(key, memory[key])

    # -------- SHORT-TERM CONTEXT MEMORY --------
    context = get_memory()
    for item in reversed(context):  # search from most recent
        content = item.get("parts", [""])[0].lower()
        if user_input in content:
            return f"You said: “{content}”"

    return f"I don’t remember anything about {user_input}."


def list_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
        if not memory:
            return "I don’t have anything in memory yet."
        return "\n".join([f"{k} is {v}" for k, v in memory.items()])
    return "I don’t have anything in memory yet."

def reset_all_memory():
    clear_memory()
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)
    return "🧹 All memory — short-term and long-term — has been cleared."
