# gpt_conversation.py

import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_SEARCH_ENABLED
from memory_engine import add_to_memory, get_memory, auto_store_facts, get_relevant_facts

# Configure API
genai.configure(api_key=GEMINI_API_KEY)

# Load model with optional Google Search grounding
if GEMINI_SEARCH_ENABLED:
    try:
        # Try to enable Google Search grounding
        google_search_tool = genai.Tool(
            function_declarations=[
                genai.FunctionDeclaration(
                    name="google_search_retrieval",
                    description="""A tool for performing Google searches to retrieve real-time information.
                    """,
                    parameters={
                        "type": "object",
                        "properties": {},
                    },
                )
            ]
        )
        # Note: This feature may require specific API access/permissions
        model = genai.GenerativeModel(
            GEMINI_MODEL,
            tools=[google_search_tool]  # Enable Google Search grounding for real-time info
        )
        print("🌐 Gemini Search enabled - Rusty can now search the web!")
    except Exception as e:
        print(f"⚠️ Could not enable Google Search: {e}")
        print("📱 Using standard Gemini model without search grounding")
        model = genai.GenerativeModel(GEMINI_MODEL)
else:
    model = genai.GenerativeModel(GEMINI_MODEL)

# Create chat object (chat history is managed by genai, no need for episodic_memory.json)
chat = model.start_chat(history=[])

def generate_response(user_input, context_keywords=None):
    """
    Generate a response using Gemini with relevant context from memory.
    
    Args:
        user_input: The user's message
        context_keywords: List of keywords for context retrieval (e.g., ["address", "birthday"])
    """
    try:
        add_to_memory("user", user_input)

        # Retrieve relevant facts from long-term memory using specific keywords
        relevant_context = get_relevant_facts(user_input, context_keywords)
        
        # Inject Rusty personality + relevant facts into prompt
        personality = (
            "You are Rusty, a chill, sarcastic, funny, but helpful assistant. "
            "Always answer like a close friend who's good with tech. Keep it short, natural, and avoid sounding robotic."
        )
        
        # Construct message with context
        if relevant_context:
            full_prompt = f"{personality}\n\n{relevant_context}\n\nUser: {user_input}"
        else:
            full_prompt = f"{personality}\n\nUser: {user_input}"

        response = chat.send_message(full_prompt)
        reply = response.text.strip()
        add_to_memory("assistant", reply)

        # AI-powered fact extraction and storage
        memory_msg = auto_store_facts(user_input)
        
        # Return both reply and memory message (if any)
        if memory_msg:
            return {"reply": reply, "memory": memory_msg}
        
        return reply

    except Exception as e:
        print("Gemini API error:", e)
        return "Rusty had a hiccup. Try again in a moment."
