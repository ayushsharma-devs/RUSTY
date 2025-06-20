
import warnings
warnings.filterwarnings("ignore")

from voice import listen, speak, listen_for_wake_word

from intent_engine.intent_router import handle_intent
from config import WAKE_WORD
import time
from gpt_conversation import generate_response
from intent_engine.detect_intent import detect_intent

from style_learning import personalize_input
print("🕒 Waiting for system to settle...")
time.sleep(5)
warnings.filterwarnings("ignore")








def log_conversation(user_input, response):
    with open("rusty_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"User: {user_input}\nRusty: {response}\n\n")



def run_assistant():
    speak("Rusty is awake. What do you want to do?")

    while True:
        user_input = listen()
        

        if not user_input or user_input == "timeout":
            speak("No input for a while. Going back to sleep.")
            break
     
        intent = detect_intent(user_input) 
        print(f"🔎 Detected Intent: {intent}")

        response = None
        if intent and intent != "chat":
            response = handle_intent(intent, user_input)
        if intent == None:
            response = generate_response(user_input)
        user_input = personalize_input(user_input)
        if isinstance(response, str):
            speak(response)
            log_conversation(user_input, response)
        elif isinstance(response, list):
            for line in response:
                speak(line)
            log_conversation(user_input, "\n".join(response))

if __name__ == "__main__":

    if listen_for_wake_word():
        run_assistant()
