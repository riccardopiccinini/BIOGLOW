import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "observations")
    INATURALIST_TOKEN = os.getenv("INATURALIST_TOKEN")
    BIRDNET_API_URL = os.getenv("BIRDNET_API_URL")
    BIRDNET_API_KEY = os.getenv("BIRDNET_API_KEY")
    
    # Modalità Demo: se True, ignora le API e restituisce dati mock
    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
    
    @classmethod
    def validate(cls):
        missing = []
        if not cls.SUPABASE_URL: missing.append("SUPABASE_URL")
        if not cls.SUPABASE_KEY: missing.append("SUPABASE_KEY")
        if missing:
            raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

config = Config()
