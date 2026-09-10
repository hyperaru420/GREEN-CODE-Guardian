from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "greencode_guardian"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GROQ_API_KEY: str = ""
    HEDERA_ACCOUNT_ID: str = ""
    HEDERA_PRIVATE_KEY: str = ""
    HEDERA_NETWORK: str = "testnet"

    # Webhooks and CI/CD
    GITHUB_WEBHOOK_SECRET: str = ""
    GITLAB_WEBHOOK_TOKEN: str = ""

    # Notifications
    SLACK_BOT_TOKEN: str = ""
    SMTP_SERVER: str = ""
    SMTP_PORT: int = 587
    SMTP_ADDRESS: str = ""
    SMTP_PASSWORD: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
