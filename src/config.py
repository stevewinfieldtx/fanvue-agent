import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FANVUE_EMAIL = os.getenv("FANVUE_EMAIL")
    FANVUE_PASSWORD = os.getenv("FANVUE_PASSWORD")
    
    RUNWARE_API_KEY = os.getenv("RUNWARE_API_KEY")
    RUNWARE_MODEL_ID = os.getenv("RUNWARE_MODEL_ID", "runware:100@1")
    
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-opus:beta")
    OPENROUTER_REFERER = os.getenv("OPENROUTER_REFERRER", "https://github.com/fanvue-agent")
    
    PROXY_URL = os.getenv("PROXY_URL")
    
    FACEBOOK_EMAIL = os.getenv("FACEBOOK_EMAIL")
    FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD")
