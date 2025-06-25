import os
import psutil
import subprocess
import re
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
saved_volume_level = None
def get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

def get_system_volume():
    saved_volume_level = get_volume_interface()
    return saved_volume_level.GetMasterVolumeLevelScalar()  # Returns 0.0 to 1.0

def set_system_volume(level):
    saved_volume_level = get_volume_interface()
    saved_volume_level.SetMasterVolumeLevelScalar(level, None)

def handle_system_command(command):
    global saved_volume_level
    command = command.lower()
    if "set volume" in command:
        match = re.search(r'\b(\d+)\b', command)
        if match:
            volume = int(match.group(1))
            scalar=volume/100
            volume=get_volume_interface()
            volume.SetMasterVolumeLevelScalar(scalar, None)
            return f"Volume set to {volume}%."
        return "Please say a number between 0 and 100."
        
    elif "unmute" in command:
        print("unmute was called")
        if saved_volume_level is not None:
            set_system_volume(saved_volume_level)
            return f"Volume restored to {int(saved_volume_level * 100)}%."
        else:
            set_system_volume(0.5)  # fallback
            return "No saved volume, setting to 50%."
    elif "mute" in command:
        print("mute was called")
        saved_volume_level = get_system_volume()  # Save current
        set_system_volume(0.0)
        return "Volume muted."

    

    elif "lock" in command:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Locking the screen."

    elif "sleep" in command:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Going to sleep."

    elif "shutdown" in command:
        os.system("shutdown /s /t 1")
        return "Shutting down. See you later!"

    elif "battery" in command:
        battery = psutil.sensors_battery()
        percent = battery.percent
        plugged = "plugged in" if battery.power_plugged else "on battery"
        return f"Battery is at {percent}% and currently {plugged}."

    elif "screenshot" in command:
        try:
            import pyautogui
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"rusty_screenshot_{timestamp}.png"
            pyautogui.screenshot(filename)
            return f"📸 Screenshot saved as {filename}."
        except Exception as e:
            return f"⚠️ Failed to take screenshot: {e}"
    

    elif "restart" in command:
        os.system("shutdown /r /t 1")
        return "Restarting the computer."
   
    else:
        return "Sorry, I didn't understand that system command."
