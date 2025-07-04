# app/config.py
import os
from dotenv import load_dotenv

# OpenAI key (keep this secret in production!)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HELICONE_API_KEY = os.getenv("HELICONE_API_KEY")

# Website to scrape
TARGET_URL = "https://woocommercegst.co.in/"

# Model name
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"


load_dotenv()  # This loads environment variables from .env

