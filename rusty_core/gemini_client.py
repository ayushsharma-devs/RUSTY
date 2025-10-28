# rusty_core/gemini_client.py

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_INTENT_MODEL, GEMINI_SEARCH_ENABLED
from google import genai
from google.genai import types

# Initialize the main client
client = genai.Client(api_key=GEMINI_API_KEY)

def get_model(model_name, use_search=False):
    """Gets a model from the client, with optional search configuration."""
    if use_search and GEMINI_SEARCH_ENABLED:
        try:
            tools = [types.Tool(google_search=types.GoogleSearch())]
            config = types.GenerateContentConfig(tools=tools)
            print(f"🌐 Gemini Search enabled for {model_name}!")
            return client.models.get(model=model_name, config=config)
        except Exception as e:
            print(f"⚠️ Could not enable Google Search for {model_name}: {e}")
            print(f"📱 Using standard {model_name} model without search grounding")
            return client.models.get(model_name)
    return client.models.get(model_name)

# --- Pre-configured models for different tasks ---

# Main model for chat conversations, with search enabled if configured
chat_model_instance = get_model(GEMINI_MODEL, use_search=True)
chat_session = chat_model_instance.start_chat(history=[])

# Model for intent detection and fact extraction (no search needed)
# Using the same model for both as they are similar tasks
intent_model_instance = get_model(GEMINI_INTENT_MODEL)
fact_extraction_model_instance = intent_model_instance