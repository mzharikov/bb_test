from pydantic import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    MONGO_URL: str
    MONGO_MAIN_DATABASE: str
    MONGO_EVENT_LOG_COLLECTION: str
    RABBITMQ_URL: str
    EXCHANGE_NAME: str
    THROTTLE_INPUT: bool
    LOG_FILE_NAME: str
    MATCH_CONFIG_FILE_NAME: str

    class Config:
        env_prefix = ""
        case_sentive = False
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore
