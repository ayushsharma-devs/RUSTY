from intent_engine.intent_map import intent_keywords
from intent_engine.gemini_intent import detect_intent_gemini

def detect_intent(user_input):
    lowered = user_input.lower()
    matched_intent = None
    matched_trigger_len = 0

    # 🧠 Try keyword-based matching first
    for intent, triggers in intent_keywords.items():
        for trigger in triggers:
            if trigger in lowered:
                if len(trigger) <= 4 and len(lowered.split()) > 3:
                    continue  # Skip vague match like "play" in long input
                if len(trigger) > matched_trigger_len:
                    matched_intent = intent
                    matched_trigger_len = len(trigger)

    # ✅ If keyword match found, return it
    if matched_intent:
        return matched_intent

    # 🔁 Otherwise, fallback to Gemini
    return detect_intent_gemini(user_input) or "chat"

