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
        
        personalized_input = personalize_input(user_input)
        if user_input != original_input:
            print(f"🔍 Personalized Input: {user_input}")
        intent = detect_intent(personalized_input)
        lowered = personalized_input.lower()

# Smart fallback remapping for missed memory triggers
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

        response = handle_intent(intent, personalized_input) if intent != "chat" else generate_response(personalized_input)

        print(f"🔍 Intent: {intent}")
        print(f"🔍 Response: {response}")

finally:
    save_memory_context()
    print("💾 Rusty's memory context saved. See you later!")
