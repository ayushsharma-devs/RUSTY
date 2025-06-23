
import os
import json

APP_DIRS = [
    os.environ["ProgramFiles"],
    os.environ["ProgramFiles(x86)"],
    os.path.expandvars(r"%LocalAppData%\Programs"),
    os.path.expandvars(r"%LocalAppData%"),
    os.path.expandvars(r"%AppData%"),
]


IGNORE_KEYWORDS = ["installer","uninstall", "helper", "setup", "update", "crash", "driver", "service", "tool", "support", "maintenance", "console", "cli", "diagnostic","plugin", "plug-in", "helper", "service", "update", "updater", "installer", "repair", "tool",
    "debug", "crash", "console", "cli", "convert", "filter", "daemon", "thumbnail", "host", "test",
    "monitor", "proxy", "agent", "viewer", "inspector", "launcher", "hook", "sync", "log", "logger",
    "token", "extractor", "utility", "sso", "updater", "renderer", "cef", "report", "manager"]

BAD_PATH_KEYWORDS = [
    "plug-ins", "plugins", "python", "lib", "helpers", "redistributable", "debug", "host", "daemon", "node_modules"
]

def is_bad_path(path):
    path = path.lower()
    return any(bad in path for bad in BAD_PATH_KEYWORDS)

def scan_apps():
    apps = {}
    for root_dir in APP_DIRS:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.lower().endswith(".exe"):
                    name = file.rsplit(".", 1)[0]
                    path = os.path.join(root, file)

                    # Filter out garbage
                    if any(word in name.lower() for word in IGNORE_KEYWORDS):
                        continue
                    if is_bad_path(path):
                        continue

                    # Avoid duplicates
                    if name not in apps:
                        apps[name] = path
    return apps

if __name__ == "__main__":
    result = scan_apps()

    print(f"Found {len(result)} likely GUI apps.")

    # FULL path
    out_path = os.path.abspath("rusty_core/app_manager/installed_apps.json")
    print(f"Saving to: {out_path}")

    try:
        os.makedirs("rusty_core/app_manager", exist_ok=True)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            print("installed_apps.json saved successfully.")

    except Exception as e:
        print("Failed to save installed_apps.json:", e)
