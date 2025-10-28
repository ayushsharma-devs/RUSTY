import json
import os
import re
from collections import deque
from difflib import get_close_matches
from datetime import datetime

# File Paths
CONTEXT_FILE = "context_memory.json"
LONG_TERM_FILE = "long_term_memory.json"

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
#delete fact
def delete_fact(key):
    key = key.lower()
    if os.path.exists(LONG_TERM_FILE):
        with open(LONG_TERM_FILE, "r") as f:
            memory = json.load(f)

        if key in memory:
            del memory[key]
            with open(LONG_TERM_FILE, "w") as f:
                json.dump(memory, f, indent=2)
            return f"🗑️ I’ve forgotten everything about {key}."
        else:
            return f"I couldn’t find anything about {key} to forget."
    return "I don’t have anything saved yet."

#reset all memory
def reset_all_memory():
    clear_memory()
    if os.path.exists(LONG_TERM_FILE):
        with open(LONG_TERM_FILE, "w") as f:
            json.dump({}, f)
    return "🧹 All memory — short-term and long-term — has been cleared."

# ---------- AI-Powered Long-Term Memory ----------

def extract_facts_ai(user_input):
    """Use Gemini to intelligently detect if user_input contains memorable facts"""
    try:
        from google.generativeai import GenerativeModel
        from config import GEMINI_API_KEY, GEMINI_INTENT_MODEL
        import google.generativeai as genai
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = GenerativeModel(GEMINI_INTENT_MODEL)
        
        prompt = f"""
You are a fact extraction AI. Analyze the user's message and determine if it contains personal information worth storing long-term.

Storable facts include:
- Birthday, age
- Name (user's or their pets/family)
- Location, address, city, country
- Job, occupation, school
- Preferences (favorite food, color, etc.)
- Important dates or events
- Contact information

If the message contains storable facts, respond ONLY in this JSON format:
{{"facts": [{{"key": "birthday", "value": "November 15"}}, {{"key": "city", "value": "Bhubaneswar"}}]}}

If NO storable facts are found, respond ONLY with:
{{"facts": []}}

User message: "{user_input}"

Response (JSON only):"""

        response = model.generate_content(prompt)
        result = response.text.strip()
        
        # Clean up the response to extract JSON
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        
        import json as json_module
        data = json_module.loads(result)
        return data.get("facts", [])
        
    except Exception as e:
        print(f"⚠️ Fact extraction error: {e}")
        return []

def auto_store_facts(user_input):
    """Automatically detect and store facts from user input"""
    facts = extract_facts_ai(user_input)
    stored = []
    
    for fact in facts:
        key = fact.get("key", "").lower().strip()
        value = fact.get("value", "").strip()
        
        if key and value:
            store_fact(key, value, context=f"extracted from: {user_input[:50]}...")
            stored.append(f"{key}: {value}")
    
    if stored:
        return f"🧠 Remembered: {', '.join(stored)}"
    return None

def get_relevant_facts(user_input, context_keywords=None):
    """
    Retrieve relevant facts from long-term memory based on context keywords.
    
    Args:
        user_input: The user's message (fallback if no keywords)
        context_keywords: List of keywords to search for (e.g., ["address", "birthday"])
    
    Returns:
        Formatted string with relevant facts or empty string
    """
    if not os.path.exists(LONG_TERM_FILE):
        return ""
    
    try:
        with open(LONG_TERM_FILE, "r") as f:
            memory = json.load(f)
        
        if not memory:
            return ""
        
        relevant = []
        
        # If we have specific keywords from intent detection, use those
        if context_keywords:
            for keyword in context_keywords:
                keyword_lower = keyword.lower()
                for key, data in memory.items():
                    # Check if keyword matches any part of the memory key
                    if keyword_lower in key.lower():
                        relevant.append(f"{key}: {data['value']}")
        else:
            # Fallback to simple keyword matching from user input
            user_lower = user_input.lower()
            for key, data in memory.items():
                # Check if any word in the key appears in the user input
                if any(word in user_lower for word in key.split()):
                    relevant.append(f"{key}: {data['value']}")
        
        if relevant:
            # Remove duplicates while preserving order
            relevant = list(dict.fromkeys(relevant))
            return "### Relevant facts from long-term memory:\n" + "\n".join(relevant)
        
        return ""
        
    except Exception as e:
        print(f"⚠️ Error retrieving facts: {e}")
        return ""
