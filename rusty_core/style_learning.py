import json
import os
import re
from difflib import get_close_matches
from collections import defaultdict

STYLE_MAP_FILE = "rusty_core/user_command_map.json"
USAGE_STATS_FILE = "rusty_core/user_command_usage.json"

# ------------------------------
# Load & Save
# ------------------------------
def load_command_map():
    if os.path.exists(STYLE_MAP_FILE):
        with open(STYLE_MAP_FILE, "r") as f:
            return json.load(f)
    return {}

def save_command_map(command_map):
    with open(STYLE_MAP_FILE, "w") as f:
        json.dump(command_map, f, indent=4)

def load_usage_stats():
    if os.path.exists(USAGE_STATS_FILE):
        with open(USAGE_STATS_FILE, "r") as f:
            return json.load(f)
    return defaultdict(int)

def save_usage_stats(stats):
    with open(USAGE_STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

# ------------------------------
# Normalization
# ------------------------------
def normalize(text):
    return " ".join(text.lower().strip().split())

def strip_prefixes(text):
    prefixes = [
        "remember that ",
        "remember ",
        "when i say ",
        "teach rusty ",
        "note that ",
    ]
    for p in prefixes:
        if text.startswith(p):
            return text[len(p):].strip()
    return text

# ------------------------------
# Verb Synonyms
# ------------------------------
VERB_SYNONYMS = {
    "open": ["launch", "start", "run"],
    "play": ["start", "listen", "queue"],
    "close": ["exit", "quit", "stop"],
}

def expand_synonyms(text):
    tokens = text.split()
    for i, token in enumerate(tokens):
        for key, synonyms in VERB_SYNONYMS.items():
            if token == key or token in synonyms:
                tokens[i] = key  # normalize to canonical verb
    return " ".join(tokens)

# ------------------------------
# Usage Stats Helper
# ------------------------------
def update_usage_stats(phrase, increment=1):
    stats = load_usage_stats()
    stats[phrase] = stats.get(phrase, 0) + increment
    save_usage_stats(stats)

# ------------------------------
# Personalize Input
# ------------------------------
def personalize_input(raw_input):
    command_map = load_command_map()
    key = normalize(raw_input)
    key = expand_synonyms(key)

    used_key = None
    # Exact match
    if key in command_map:
        used_key = key
        result = command_map[key]
    else:
        # Fuzzy match
        matches = get_close_matches(key, command_map.keys(), n=1, cutoff=0.7)
        if matches:
            used_key = matches[0]
            result = command_map[matches[0]]
        else:
            # Partial token match
            result = raw_input
            for shortcut, full_cmd in command_map.items():
                if key in shortcut.split():
                    used_key = shortcut
                    result = full_cmd
                    break

    # Update usage stats exactly once
    if used_key:
        update_usage_stats(used_key)
    else:
        update_usage_stats(key, increment=1)

    return result

# ------------------------------
# Teach a new custom command
# ------------------------------
def teach_command(text):
    try:
        lowered = normalize(text)
        lowered = strip_prefixes(lowered)
        lowered = expand_synonyms(lowered)

        # regex patterns: "X means Y", "X it means Y", "X → Y", "X is Y"
        match = re.search(r"(.+?)\s*(it means|means|→|is)\s*(.+)", lowered)
        if not match:
            return "Please use the format: 'X means Y', 'X it means Y', 'X → Y' or 'X is Y'."

        shortcut, _, full_command = match.groups()
        shortcut = normalize(expand_synonyms(shortcut))
        full_command = normalize(expand_synonyms(full_command.strip()))

        command_map = load_command_map()

        # Overwrite warning
        if shortcut in command_map:
            old = command_map[shortcut]
            command_map[shortcut] = full_command
            save_command_map(command_map)
            return f"⚠️ Updated: '{shortcut}' now means '{full_command}' (was '{old}')."

        command_map[shortcut] = full_command
        save_command_map(command_map)
        return f"🧠 Got it! When you say '{shortcut}', I'll take it as '{full_command}'."

    except Exception as e:
        return f"⚠️ Error while learning: {e}"
