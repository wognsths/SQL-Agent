import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Setting application"""
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    database_url: str = os.getenv("DATABASE_URL", "")

    output_dir: str = os.getenv("OUTPUT_DIR", "outputs")

    class Config:
        env_file = ".env"

settings = Settings()

# Make directory
os.makedirs(settings.output_dir, exist_ok=True)