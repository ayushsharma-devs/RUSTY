from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Expose configs globally
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WAKE_WORD = os.getenv("WAKE_WORD", "hey bro")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")