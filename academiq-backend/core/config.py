from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AcademiQ"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # JWT Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@academiq.com"

    # ML
    MODEL_PATH: str = "ml/models/risk_model_v1.pkl"

    # CORS
    FRONTEND_URL: str = "http://localhost:5174"

    class Config:
        env_file = ".env"

settings = Settings()