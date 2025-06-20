import json
import os
from collections import deque

# Files
MEMORY_FILE = "rusty_memory.json"        # long-term memory
CONTEXT_FILE = "rusty_context.json"      # short-term context memory

# Short-term memory (context window)
memory_buffer = deque(maxlen=20)

# ---------- Context Memory Functions ----------
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

# ---------- Long-term Memory Functions ----------
def remember(key, value):
    memory = {}
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    memory[key.lower()] = value
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)
    return f"Got it. I’ll remember that {key} is {value}."

import re

def recall(user_input):
    # Load memory
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)

    # Clean user input
    user_input = user_input.lower().strip()
    user_input = re.sub(r'[^\w\s]', '', user_input)  # remove punctuation

    # Try exact match first
    if user_input in memory:
        return memory[user_input]

    # Fuzzy match: look for partial matches
    for key in memory:
        if key in user_input or user_input in key:
            return memory[key]

    return f"I don’t remember anything about {user_input}."


def forget(key):
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
        if key.lower() in memory:
            del memory[key.lower()]
            with open(MEMORY_FILE, "w") as f:
                json.dump(memory, f, indent=4)
            return f"Alright, I forgot {key}."
    return f"I don’t remember anything about {key}."

def list_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
        if not memory:
            return "I don’t have anything in memory yet."
        return "\n".join([f"{k} is {v}" for k, v in memory.items()])
    return "I don’t have anything in memory yet."

# ---------- Total Reset ----------
def reset_all_memory():
    clear_memory()
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)
    return "All memory — short-term and long-term — has been cleared."
