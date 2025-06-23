import subprocess
import json
import os
import psutil  # pip install psutil
from difflib import get_close_matches
import re
json_path = os.path.join(os.path.dirname(__file__), "installed_apps.json")
with open(json_path, "r") as f:
    # Load installed apps JSON
    INSTALLED_APPS = json.load(f)
def normalize_name(name):
    return name.lower().replace(" ", "").replace(".exe", "")

import re

# Optional shortcut words users might use
APP_SYNONYMS = {
    "dc": "discord",
    "vscode": "code",
    "vs code": "code",
    "word": "microsoft word",
    "ppt": "powerpoint",
    "chrome": "google chrome",
    "yt": "youtube"
}

# Phrases you might want to strip from start or end
TRAILING_NOISE = ["please", "for me", "right now", "thanks", "thank you", "bro", "now"]

def extract_app_name(text):
    text = text.lower().strip()

    # Strip common polite starters
    text = re.sub(r"^(can you|could you|would you|please|hey|rusty)\s+", "", text)

    # Find pattern like "open xyz", "start xyz", etc.
    match = re.search(r"(?:open|start|launch)\s+(.+)", text)
    if not match:
        return None

    raw_app = match.group(1).strip()

    # Remove trailing junk
    for phrase in TRAILING_NOISE:
        if raw_app.endswith(phrase):
            raw_app = raw_app[: -len(phrase)].strip()

    # Replace with synonym if matched
    if raw_app in APP_SYNONYMS:
        raw_app = APP_SYNONYMS[raw_app]

    return raw_app
def get_best_match(user_input):
    from difflib import get_close_matches

    query = normalize_name(user_input)

    normalized_apps = {normalize_name(name): name for name in INSTALLED_APPS}

    if query in normalized_apps:
        return normalized_apps[query]

    prefix_matches = [original for norm, original in normalized_apps.items() if norm.startswith(query)]
    if prefix_matches:
        return prefix_matches[0]

    substring_matches = [original for norm, original in normalized_apps.items() if query in norm]
    if substring_matches:
        return substring_matches[0]

    fuzzy_matches = get_close_matches(query, normalized_apps.keys(), n=1, cutoff=0.6)
    if fuzzy_matches:
        return normalized_apps[fuzzy_matches[0]]

    return None


def open_app(app_name):
    matched_name = get_best_match(app_name)
    if matched_name:
        path = INSTALLED_APPS[matched_name]
        try:
            subprocess.Popen(path)
            return f"✅ Opening {matched_name}."
        except Exception as e:
            return f"❌ Failed to open {matched_name}: {e}"
    return f"⚠️ Couldn't find anything matching '{app_name}'."

def close_app(app_name):
    matched_name = get_best_match(app_name)
    if not matched_name:
        return f"⚠️ Couldn't find anything matching '{app_name}'."

    exe_name = os.path.basename(INSTALLED_APPS[matched_name])
    found = False
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == exe_name.lower():
                proc.kill()
                found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if found:
        return f"✅ Closed {matched_name}."
    else:
        return f"❌ Couldn't find {matched_name} running."
