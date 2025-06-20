from intent_engine.detect_intent import detect_intent
from intent_engine.intent_router import handle_intent
from memory import load_memory_context, save_memory_context, reset_all_memory
from gpt_conversation import generate_response
from style_learning import personalize_input

print("🧪 Rusty Test Mode (Text Only) — type 'exit' to quit or 'reset all' to clear memory.")

# Load short-term context memory
load_memory_context()

try:
    while True:
        user_input = input("🧠 You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break
        elif user_input.lower() == "reset all":
            print("🧹", reset_all_memory())
            continue
        original_input = user_input
        # Detect intent (local or Gemini fallback)
        intent = detect_intent(user_input)
        print(f"🔍 Intent Detected: {intent}")
        user_input = personalize_input(user_input)
        if user_input != original_input:
            print(f"🔍 Personalized Input: {user_input}")
        response = None

        # Only handle non-chat intents
        if intent and intent != "chat":
            response = handle_intent(intent, user_input)

        # If no valid handler or intent is chat → use Gemini to reply
        if response is None:
            response = generate_response(user_input)

        print("🤖 Rusty:", response)

finally:
    save_memory_context()
    print("💾 Rusty's memory context saved. See you later!")
