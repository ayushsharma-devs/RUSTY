import json
import os
from difflib import get_close_matches
STYLE_MAP_FILE = "rusty_core/user_command_map.json"

# Load saved user phrase → real command mappings
def load_command_map():
    if os.path.exists(STYLE_MAP_FILE):
        with open(STYLE_MAP_FILE, "r") as f:
            return json.load(f)
    return {}

# Save updated command mappings
def save_command_map(command_map):
    with open(STYLE_MAP_FILE, "w") as f:
        json.dump(command_map, f, indent=4)

# Replace shortcut with learned full command (if it exists)

def personalize_input(raw_input):
    command_map = load_command_map()
    key = normalize(raw_input)
    if key in command_map:
        return command_map[key]
    # fallback fuzzy match
    matches = get_close_matches(key, command_map.keys(), n=1, cutoff=0.7)
    if matches:
        return command_map[matches[0]]
    return raw_input

def normalize(text):
    return " ".join(text.lower().strip().split())
# Learn a new custom command
def teach_command(text):
    import re
    try:
        lowered = text.lower()
        # regex patterns: "X means Y", "X it means Y", "X → Y", "X is Y"
        match = re.search(r'(.+?)\s*(it means|means|→|is)\s*(.+)', lowered)
        if not match:
            return "Please use the format: 'X means Y', 'X it means Y', 'X → Y' or 'X is Y'."

        shortcut, _, full_command = match.groups()
        shortcut = normalize(shortcut)
        full_command = full_command.strip()

        command_map = load_command_map()

        if shortcut in command_map:
            return f"'{shortcut}' already exists as '{command_map[shortcut]}'. Use a new phrase or overwrite."

        command_map[shortcut] = full_command
        save_command_map(command_map)
        return f"🧠 Got it! When you say '{shortcut}', I'll take it as '{full_command}'."

    except Exception as e:
        return f"⚠️ Error while learning: {e}"
