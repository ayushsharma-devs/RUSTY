import re
from intent_engine.gemini_intent import detect_intent_gemini
from intent_engine.intent_map import intent_keywords

def detect_intent(user_input):
    """
    Returns a dict: {"intent": "intent_name", "context_needed": ["keyword1", "keyword2"]}
    """
    lowered = user_input.lower().strip()

    # Special disambiguation for "remember that ... means ..."
    if re.search(r"remember that .* means", lowered):
        return {"intent": "teach_command", "context_needed": []}

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
        # Keyword-based match doesn't determine context_needed, so empty array
        return {"intent": matched_intent, "context_needed": []}

    # Fallback to AI-based detection (returns dict with both intent and context_needed)
    result = detect_intent_gemini(user_input)
    return result if isinstance(result, dict) else {"intent": result or "chat", "context_needed": []}
