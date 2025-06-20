import warnings
warnings.filterwarnings("ignore")
import threading
from voice import listen, speak
from intent_engine.intent_router import handle_intent
import time
from gpt_conversation import generate_response
from intent_engine.detect_intent import detect_intent
from style_learning import personalize_input,teach_command

print("🕒 Waiting for system to settle...")
time.sleep(3)

MAX_ACTIVE_THREADS = 10
active_threads = []

def log_conversation(user_input, response):
    with open("rusty_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"User: {user_input}\nRusty: {response}\n\n")

def threaded_response(user_input):
    try:
        if user_input.lower().strip() in ["exit", "end"]:
            speak("Shutting down.")
            print("👋 Exit command received.")
            exit(0)

        # 🧠 Check for teaching phrase first
        if " it means " in user_input.lower() or " means " in user_input.lower():
            result = teach_command(user_input)
            speak(result)
            log_conversation(user_input, result)
            return

        # 🧠 Personalize input next (if a match exists)
        personalized_input = personalize_input(user_input)

        # 🎯 Detect intent and respond  
        intent = detect_intent(personalized_input)
        print(f"🔎 Detected Intent: {intent}")

        response = None
        if intent and intent != "chat":
            response = handle_intent(intent, personalized_input)
        if intent is None or intent == "chat":
            response = generate_response(personalized_input)

        # 🗣️ Speak and log
        if isinstance(response, str):
            speak(response)
            log_conversation(personalized_input, response)
        elif isinstance(response, list):
            for line in response:
                speak(line)
            log_conversation(personalized_input, "\n".join(response))

    finally:
        active_threads.remove(threading.current_thread())
def run_assistant():
    MAX_TIMEOUTS = 2
    timeouts = 0
    speak("Rusty is awake and listening.")
    while True:
        user_input = listen()
        if not user_input or user_input == "timeout":
            timeouts += 1
            if timeouts >= MAX_TIMEOUTS:
                speak("No input for a while. Going back to sleep.")
                break
            else:
                speak("I'm still here. What can I do for you?")
                continue
        timeouts = 0
        if len(active_threads) < MAX_ACTIVE_THREADS:
            t = threading.Thread(target=threaded_response, args=(user_input,), daemon=True)
            t.start()
            active_threads.append(t)
        else:
            print("⚠️ Too many requests running.")
            speak("I'm still working on your last commands. Please wait a bit.")

if __name__ == "__main__":
    run_assistant()
