from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GEMINI_API_KEY: str
    MONGO_URI: str
    REDIS_URL: str
    # GOOGLE_MAPS_API_KEY: str
    BREVO_API_KEY: str
    ENV: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()