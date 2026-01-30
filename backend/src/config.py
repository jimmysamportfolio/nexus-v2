import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # llm client
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_AI_MODEL = "liquid/lfm-2.5-1.2b-thinking:free"
    MAX_RETRIES = 3
    DEFAULT_PROMPT = "Hello, tell me a short joke."


    
config = Config()