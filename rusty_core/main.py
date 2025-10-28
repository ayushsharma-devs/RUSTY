import warnings
warnings.filterwarnings("ignore")

import threading
import time
import queue
import uuid
from voice_engine import listen, speak, init_voice_engine
from intent_engine.intent_router import handle_intent
from gpt_conversation import generate_response
from intent_engine.detect_intent import detect_intent
from style_learning import personalize_input, teach_command

print("🕒 Waiting for system to settle...")
time.sleep(3)

# 🧠 Priority mapping
INTENT_PRIORITY = {
    "mute": 0,
    "unmute": 0,
    "lock": 0,
    "shutdown": 0,
    "sleep": 0,
    "pause_music": 0,
    "recall_fact": 0,
    "remember_fact": 0,
    "recall_recent": 0,
    "list_memory": 0,
    "clear_memory": 0,

    "open_app": 1,
    "close_app": 1,
    "play_music": 1,
    "resume_music": 1,
    "next_song": 1,
    "prev_song": 1,

    "chat": 2  # Lowest priority
}

# 🧵 Shared state
priority_queue = queue.PriorityQueue()
current_task = None
current_task_lock = threading.Lock()

# 🧩 Task class with cancel flag
class PriorityTask:
    def __init__(self, priority, user_input):
        self.priority = priority
        self.user_input = user_input
        self.should_stop = threading.Event()
        self.id = uuid.uuid4()  # for debug

    def __lt__(self, other):
        return self.priority < other.priority

def log_conversation(user_input, response):
    with open("rusty_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"User: {user_input}\nRusty: {response}\n\n")

def threaded_response(task):
    user_input = task.user_input

    if user_input.lower().strip() in ["exit", "end"]:
        speak("Shutting down.")
        print("👋 Exit command received.")
        exit(0)

    if " it means " in user_input.lower() or " means " in user_input.lower():
        result = teach_command(user_input)
        speak(result)
        log_conversation(user_input, result)
        return

    personalized_input = personalize_input(user_input)
    lowered = personalized_input.lower()
    intent_data = detect_intent(personalized_input)
    
    # Extract intent and context keywords
    if isinstance(intent_data, dict):
        intent = intent_data.get("intent", "chat")
        context_keywords = intent_data.get("context_needed", [])
    else:
        # Backwards compatibility
        intent = intent_data
        context_keywords = []

    # Intent override
    
    if intent == "chat":
        if "what did i say about" in lowered:
            intent = "recall_recent"
        elif lowered.startswith("remember") or "remember that" in lowered:
            intent = "remember_fact"
        elif lowered.startswith("forget") or "forget what i told you about" in lowered:
            intent = "forget_fact"
        elif lowered.startswith("what is") or "what do you remember" in lowered:
            intent = "recall_fact"
        elif lowered.startswith("list memory") or lowered.startswith("show memory"):
            intent = "list_memory"
        elif lowered.startswith("clear memory") or lowered.startswith("reset memory"):
            intent = "clear_memory"

    # If task was cancelled mid-way
    if task.should_stop.is_set():
        print(f"🛑 Task {task.id} was cancelled before execution.")
        return

    # 🔁 Main response logic - pass context keywords to generate_response for chat intent
    response = handle_intent(intent, personalized_input) if intent != "chat" else generate_response(personalized_input, context_keywords)

    if task.should_stop.is_set():
        print(f"🛑 Task {task.id} was cancelled before speaking.")
        return

    if isinstance(response, str):
        speak(response)
        log_conversation(personalized_input, response)
    elif isinstance(response, list):
        for line in response:
            if task.should_stop.is_set():
                print(f"🛑 Task {task.id} interrupted mid-response.")
                return
            speak(line)
        log_conversation(personalized_input, "\n".join(response))

def worker_loop():
    global current_task
    while True:
        new_task = priority_queue.get()

        with current_task_lock:
            if current_task and current_task.priority > new_task.priority:
                print("⚠️ Preempting low-priority task.")
                current_task.should_stop.set()
                time.sleep(0.2)  # Give old thread time to exit

            current_task = new_task

        t = threading.Thread(target=threaded_response, args=(new_task,), daemon=True)
        t.start()
        t.join()  # Wait until task is fully done

        with current_task_lock:
            current_task = None

def run_assistant():
    init_voice_engine()
    speak("Rusty is awake and listening.")
    time.sleep(1)

    # Start worker thread
    threading.Thread(target=worker_loop, daemon=True).start()

    while True:
        user_input = listen()
        if not user_input:
            speak("I didn’t catch that. Try again.")
            continue

        # Assign priority
        intent_data = detect_intent(personalize_input(user_input))
        # Extract intent from dict
        intent = intent_data.get("intent", "chat") if isinstance(intent_data, dict) else intent_data
        priority = INTENT_PRIORITY.get(intent, 1)

        task = PriorityTask(priority, user_input)
        priority_queue.put(task)

if __name__ == "__main__":
    run_assistant()
