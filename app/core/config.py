import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "super-secret-key-change-me",
    )

    GMAIL_ADDRESS: str = os.getenv(
        "GMAIL_ADDRESS",
        "",
    )

    GMAIL_APP_PASSWORD: str = os.getenv(
        "GMAIL_APP_PASSWORD",
        "",
    )

    class Config:
        env_file = ".env"


settings = Settings()