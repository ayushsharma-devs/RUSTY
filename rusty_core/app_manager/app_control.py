import subprocess
import json
import os
import psutil  # pip install psutil
from difflib import get_close_matches

# Load installed apps JSON
with open("app_manager/installed_apps.json", "r") as f:
    INSTALLED_APPS = json.load(f)

def normalize_name(name):
    return name.lower().replace(" ", "").replace(".exe", "")

def get_best_match(app_name):
    app_names = list(INSTALLED_APPS.keys())
    normalized_app_names = list(map(normalize_name, app_names))
    matches = get_close_matches(normalize_name(app_name), normalized_app_names, n=1, cutoff=0.6)
    if matches:
        index = normalized_app_names.index(matches[0])
        return app_names[index]  # Return original app name
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
