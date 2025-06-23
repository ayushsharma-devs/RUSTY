from intent_engine.intent_map import intent_keywords
from intent_engine.gemini_intent import detect_intent_gemini

def detect_intent(user_input):
    lowered = user_input.lower()
    matched_intent = None
    matched_trigger_len = 0

    for intent, triggers in intent_keywords.items():
        for trigger in triggers:
            if trigger in lowered:
                # Avoid short words like "play" or "next" unless it's a full command
                if len(trigger) <= 4 and len(lowered.split()) > 3:
                    continue  # Skip vague match like "play" in long input

                if len(trigger) > matched_trigger_len:
                    matched_intent = intent
                    matched_trigger_len = len(trigger)

    return matched_intent or "chat"
