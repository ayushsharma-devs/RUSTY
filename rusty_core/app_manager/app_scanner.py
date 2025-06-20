
import os
import json

APP_DIRS = [
    os.environ["ProgramFiles"],
    os.environ["ProgramFiles(x86)"],
    os.path.expandvars(r"%LocalAppData%\Programs"),
    os.path.expandvars(r"%LocalAppData%"),
    os.path.expandvars(r"%AppData%"),
]

IGNORE_KEYWORDS = ["installer","uninstall", "helper", "setup", "update", "crash", "driver", "service", "tool", "support", "maintenance", "console", "cli", "diagnostic"]

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

                    # Avoid duplicates
                    if name not in apps:
                        apps[name] = path
    return apps

if __name__ == "__main__":
    result = scan_apps()

    # Save in app_manager folder
    with open("app_manager/installed_apps.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"✅ Found {len(result)} apps.")
