import re
from intent_engine.gemini_intent import detect_intent_gemini
from intent_engine.intent_map import intent_keywords
def detect_intent(user_input):
    lowered = user_input.lower().strip()

    # Special disambiguation for "remember that ... means ..."
    if re.search(r"remember that .* means", lowered):
        return "teach_command"

    matched_intent = None
    matched_trigger_len = 0

    for intent, triggers in intent_keywords.items():
        for trigger in triggers:
            if trigger in lowered:
                if len(trigger) <= 4 and len(lowered.split()) > 3:
                    continue
                if len(trigger) > matched_trigger_len:
                    matched_intent = intent
                    matched_trigger_len = len(trigger)

    if matched_intent:
        return matched_intent

    return detect_intent_gemini(user_input) or "chat"
