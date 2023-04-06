from pydantic import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    RABBITMQ_URL: str
    EXCHANGE_NAME: str
    MATCH_CONFIG_FILE_NAME: str

    class Config:
        env_prefix = ""
        case_sentive = False
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore
