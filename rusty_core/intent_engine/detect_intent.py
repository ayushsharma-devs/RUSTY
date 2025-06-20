from intent_engine.intent_map import intent_keywords
from intent_engine.gemini_intent import detect_intent_gemini

def detect_intent(user_input):
    user_input = user_input.lower()
    if any(kw in user_input for kw in ["it means", " means "]) and any(prefix in user_input  for prefix in ["when i say", "remember that", "teach rusty"]):
        return "teach_command"

    # First try keyword-based matching
    for intent, phrases in intent_keywords.items():
        for phrase in sorted(phrases, key=lambda x: -len(x)):
            if phrase in user_input:
    
                return intent

    # Fallback to Gemini-based detection
    return detect_intent_gemini(user_input)
