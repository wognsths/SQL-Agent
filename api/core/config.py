import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ---- Project ----
    PROJECT_NAME: str = "Text2SQL A2A"
    VERSION: str = "0.1.0"

    # ---- OpenAI ----
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # ---- Database ----
    POSTGRES_USER: str = os.getenv("DB_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    POSTGRES_HOST: str = os.getenv("DB_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("DB_PORT", "5432")
    POSTGRES_DB: str = os.getenv("DB_NAME", "postgres")

    @property
    def DATABASE_URL(self) -> str:  # noqa: N802
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ---- API ----
    API_HOST: str = os.getenv("HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("PORT", "8000"))

    # ---- Output ----
    OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")

    # ---- Logging ----
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Pydantic‑settings v2 style
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
