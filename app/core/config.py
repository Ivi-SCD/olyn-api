from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GOOGLE_MAPS_API_KEY: str
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""

    APP_NAME: str = "Olyn"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False


settings = Settings()  # type: ignore[call-arg]
