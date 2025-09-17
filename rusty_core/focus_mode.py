import time
import threading
import system_control as sc
import spotify_control as sp
# Track focus state globally
FOCUS_STATE = {
    "enabled": False,
    "end_time": None,
    "mode": None
}

# Core toggle
def toggle_focus(mode="focus", duration=None):
    global FOCUS_STATE
    if FOCUS_STATE["enabled"]:
        # Turn OFF
        FOCUS_STATE = {"enabled": False, "end_time": None, "mode": None}
        # Add system hooks here (unmute sounds, clear status, etc.)
        sp.play_music("https://open.spotify.com/playlist/37i9dQZF1DX7EF8wVxBVhG?si=0289f7c047004582")
        
        return f"🟢 Focus mode disabled."
    else:
        # Turn ON
        FOCUS_STATE["enabled"] = True
        FOCUS_STATE["mode"] = mode
        if duration:
            FOCUS_STATE["end_time"] = time.time() + duration * 60
            threading.Thread(target=_auto_disable, daemon=True).start()
        # Add system hooks here (mute sounds, pause notifications, play playlist, etc.)
        return f"🔴 {mode.title()} mode enabled{' for ' + str(duration) + ' minutes' if duration else ''}."

# Auto turn-off after duration
def _auto_disable():
    global FOCUS_STATE
    while FOCUS_STATE["enabled"] and FOCUS_STATE["end_time"]:
        if time.time() >= FOCUS_STATE["end_time"]:
            FOCUS_STATE = {"enabled": False, "end_time": None, "mode": None}
            print("🟢 Focus mode automatically disabled.")
            break
        time.sleep(5)

# Status check
def check_focus():
    if FOCUS_STATE["enabled"]:
        if FOCUS_STATE["end_time"]:
            remaining = int(FOCUS_STATE["end_time"] - time.time())
            mins, secs = divmod(remaining, 60)
            return f"🔴 {FOCUS_STATE['mode'].title()} mode is active. Ends in {mins}m {secs}s."
        return f"🔴 {FOCUS_STATE['mode'].title()} mode is active (no timer)."
    return "🟢 Focus mode is off."
