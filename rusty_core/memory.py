import json
import os
import re
from collections import deque
from difflib import get_close_matches
from datetime import datetime

# File Paths
CONTEXT_FILE = "rusty_core/rusty_context.json"
LONG_TERM_FILE = "rusty_core/data/long_term_memory.json"
EPISODE_FILE = "rusty_core/data/episodic_memory.json"

# Short-term buffer
memory_buffer = deque(maxlen=20)

# ---------- Short-Term Memory ----------

def add_to_memory(role, content):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "parts": [content]
    }
    memory_buffer.append(entry)

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
    topic = topic.lower()
    for msg in reversed(memory_buffer):
        if msg["role"] == "user" and topic in msg["parts"][0].lower():
            return msg["parts"][0]
    return None

# ---------- Long-Term Memory ----------

def store_fact(key, value, context="user provided"):
    key = key.lower()
    memory = {}
    if os.path.exists(LONG_TERM_FILE):
        with open(LONG_TERM_FILE, "r") as f:
            memory = json.load(f)

    memory[key] = {
        "value": value,
        "origin": "user",
        "timestamp": datetime.now().isoformat(),
        "context": context
    }

    with open(LONG_TERM_FILE, "w") as f:
        json.dump(memory, f, indent=2)

    return f"🧠 Got it. I’ll remember that {key} is {value}."

def query_fact(user_input):
    user_input = user_input.lower().strip()
    user_input = re.sub(r"[^\w\s]", "", user_input)

    if os.path.exists(LONG_TERM_FILE):
        with open(LONG_TERM_FILE, "r") as f:
            memory = json.load(f)

        if user_input in memory:
            return rephrase_fact(user_input, memory[user_input]["value"])

        close_keys = get_close_matches(user_input, memory.keys(), n=1, cutoff=0.6)
        if close_keys:
            key = close_keys[0]
            return rephrase_fact(key, memory[key]["value"])

    context = get_memory()
    for item in reversed(context):
        content = item.get("parts", [""])[0].lower()
        if user_input in content:
            return f"You said: “{content}”"

    return f"I don’t remember anything about {user_input}."

def rephrase_fact(key, value):
    templates = {
        "name": "Your name is {}.",
        "birthday": "Your birthday is {}.",
        "city": "You said you live in {}.",
        "location": "You're in {}.",
        "dog": "Your dog's name is {}.",
        "cat": "Your cat's name is {}."
    }
    for trigger, template in templates.items():
        if trigger in key:
            return template.format(value.capitalize())
    return f"You told me that {key} is {value}."

def list_memory():
    if os.path.exists(LONG_TERM_FILE):
        with open(LONG_TERM_FILE, "r") as f:
            memory = json.load(f)
        if not memory:
            return "I don’t have anything in memory yet."
        return "\n".join([f"{k} is {v['value']}" for k, v in memory.items()])
    return "I don’t have anything in memory yet."

def reset_all_memory():
    clear_memory()
    for file in [LONG_TERM_FILE, EPISODE_FILE]:
        if os.path.exists(file):
            with open(file, "w") as f:
                json.dump({}, f)
    return "🧹 All memory — short-term and long-term — has been cleared."

# ---------- Episodic Memory ----------

def store_episode(topic, user_line, assistant_line, tags=[]):
    episode = {
        "topic": topic,
        "user": user_line,
        "assistant": assistant_line,
        "timestamp": datetime.now().isoformat(),
        "tags": tags
    }

    data = []
    if os.path.exists(EPISODE_FILE):
        with open(EPISODE_FILE, "r") as f:
            data = json.load(f)

    data.append(episode)
    with open(EPISODE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def query_episode(topic):
    topic = topic.lower()
    if os.path.exists(EPISODE_FILE):
        with open(EPISODE_FILE, "r") as f:
            episodes = json.load(f)
        results = [ep for ep in episodes if topic in ep["topic"].lower() or topic in ep.get("user", "")]
        if results:
            return "\n".join([f"You: {r['user']}\nMe: {r['assistant']}" for r in results[-3:]])
    return "I don’t remember discussing that before."
