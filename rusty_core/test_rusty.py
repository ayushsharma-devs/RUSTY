import threading
import queue
import time
import uuid
import sys

from intent_engine.detect_intent import detect_intent
from intent_engine.intent_router import handle_intent
from memory_engine import load_memory_context, save_memory_context, reset_all_memory
from gpt_conversation import generate_response
from intent_engine.intent_map import intent_keywords
from style_learning import personalize_input

# 🎯 Priority mapping
INTENT_PRIORITY = {
    "mute": 0, "unmute": 0, "lock": 0, "shutdown": 0, "sleep": 0,
    "pause_music": 0, "recall_fact": 0, "remember_fact": 0,
    "recall_recent": 0, "list_memory": 0, "clear_memory": 0,

    "open_app": 1, "close_app": 1, "play_music": 1,
    "resume_music": 1, "next_song": 1, "prev_song": 1,

    "chat": 2
}

# 🧵 Shared state
priority_queue = queue.PriorityQueue()
current_task = None
current_task_lock = threading.Lock()
print_lock = threading.Lock()  # Prevents stdout conflicts during debugging


# 🖨️ Thread-safe print (fixes debugger + input() conflicts)
def safe_print(*args, **kwargs):
    """Thread-safe print to prevent stdout conflicts with input()"""
    with print_lock:
        print(*args, **kwargs)
        sys.stdout.flush()


# 🧩 Task object
class PriorityTask:
    def __init__(self, priority, user_input):
        self.priority = priority
        self.user_input = user_input
        self.should_stop = threading.Event()
        self.id = uuid.uuid4()

    def __lt__(self, other):
        return self.priority < other.priority


# 🎬 Task execution logic
def threaded_response(task: PriorityTask):
    if task.should_stop.is_set():
        safe_print(f"🛑 Task {task.user_input} cancelled before starting.")
        return

    personalized_input = personalize_input(task.user_input)
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

    # Intent override logic
    if intent == "chat":
        if "what did i say about" in lowered:
            intent = "recall_recent"
        elif lowered.startswith("remember") or "remember that" in lowered:
            intent = "remember_fact"
        elif lowered.startswith("forget") or "forget what i told you about" in lowered:
            intent = "forget_fact"
        elif lowered.startswith("what is") or "what do you remember" in lowered:
            intent = "recall_fact"
        elif "list memory" in lowered or "show memory" in lowered:
            intent = "list_memory"
        elif "clear memory" in lowered or "reset memory" in lowered:
            intent = "clear_memory"

    if task.should_stop.is_set():
        safe_print(f"🛑 Task {task.user_input} cancelled mid-processing.")
        return
    
    # Show intent and context keywords if available
    if context_keywords:
        safe_print(f"🔍 Intent: {intent} | Context: {', '.join(context_keywords)}")
    else:
        safe_print(f"🔍 Intent: {intent}")
    
    # Handle intent - pass context keywords to generate_response for chat intent
    response = handle_intent(intent, personalized_input) if intent != "chat" else generate_response(personalized_input, context_keywords)

    if task.should_stop.is_set():
        safe_print(f"🛑 Task {task.user_input} cancelled before response output.")
        return

    # Handle response (can be string, dict, or list)
    memory_msg = None
    if isinstance(response, dict):
        memory_msg = response.get("memory")
        response = response.get("reply", "")
    
    # Output response
    if isinstance(response, str):
        for line in response.split("\n"):
            if task.should_stop.is_set():
                safe_print(f"🛑 Task {task.user_input} interrupted mid-response.")
                return
            safe_print(f"🧠 Rusty: {line}")
            time.sleep(0.2)
    elif isinstance(response, list):
        for line in response:
            if task.should_stop.is_set():
                safe_print(f"🛑 Task {task.user_input} interrupted mid-response list.")
                return
            safe_print(f"🧠 Rusty: {line}")
            time.sleep(0.1)  # Simulate output pacing
    
    # Show memory message if facts were stored
    if memory_msg:
        safe_print(memory_msg)


def run_task(task: PriorityTask):
    """Wrapper that executes one task and clears scheduler pointer."""
    threaded_response(task)
    # mark done only if we’re still the current task
    with current_task_lock:
        if current_task is task:
            # task truly finished (wasn’t pre‑empted later)
            globals()["current_task"] = None

def worker_loop():
    global current_task
    while True:
        task = priority_queue.get()

        with current_task_lock:
            # if something is already running AND has lower priority → cancel it
            if current_task and current_task.priority > task.priority:
                safe_print("⚠️ Pre‑empting lower‑priority task.")
                current_task.should_stop.set()

            # we now become the active task
            current_task = task

        safe_print(f"\n🎬 Executing: {task.user_input} (Priority {task.priority})")

        # fire‑and‑forget thread—no join, so higher‑priority tasks can queue & run
        threading.Thread(target=run_task, args=(task,), daemon=True).start()

# 🚀 Entry point
def main():
    print("🧪 Rusty Test Mode (Priority Enabled) — type 'exit' to quit or 'reset all' to clear memory.")
    load_memory_context()

    threading.Thread(target=worker_loop, daemon=True).start()

    try:
        while True:
            # Print prompt separately with thread-safe print to avoid mixing with background output
            with print_lock:
                sys.stdout.write("\n🧠 You: ")
                sys.stdout.flush()
            
            user_input = input().strip()
            
            if user_input.lower() in ["exit", "quit"]:
                break
            elif user_input.lower() == "reset all":
                safe_print("🧹", reset_all_memory())
                continue

            intent_data = detect_intent(personalize_input(user_input))
            # Extract intent from dict
            intent = intent_data.get("intent", "chat") if isinstance(intent_data, dict) else intent_data
            priority = INTENT_PRIORITY.get(intent, 1)

            task = PriorityTask(priority, user_input)
            safe_print(f"📥 Queued: {user_input} (Priority {priority})")
            priority_queue.put(task)

    finally:
        save_memory_context()
        print("💾 Rusty's memory context saved. See you later!")


if __name__ == "__main__":
    main()
