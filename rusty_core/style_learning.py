import json
import os

STYLE_MAP_FILE = "user_command_map.json"

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
    return command_map.get(raw_input.lower().strip(), raw_input)

# Learn a new custom command
def teach_command(text):
    try:
        lowered = text.lower()

        # Accept either "it means" or just "means"
        if " it means " in lowered:
            parts = lowered.split(" it means ", 1)
        elif " means " in lowered:
            parts = lowered.split(" means ", 1)
        else:
            return "Please use the format: 'X means Y' or 'when I say X it means Y'"

        if len(parts) != 2:
            return "Couldn't parse your command properly."

        shortcut = parts[0]
        full_command = parts[1]

        # Strip known prefixes (from intent_map)
        for prefix in ["when i say", "remember that", "teach rusty"]:
            if shortcut.strip().startswith(prefix):
                shortcut = shortcut.replace(prefix, "").strip()

        shortcut = shortcut.strip()
        full_command = full_command.strip()

        if shortcut and full_command:
            command_map = load_command_map()
            command_map[shortcut] = full_command
            save_command_map(command_map)
            return f"🧠 Got it! When you say '{shortcut}', I'll take it as '{full_command}'."
        else:
            return "Couldn't extract both shortcut and full command."
    except Exception as e:
        return f"⚠️ Error while learning: {e}"
