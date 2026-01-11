from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from enum import Enum


class VectorTables(Enum):
    SOLUTIONS = "solution_vectors"
    INTERACTIONS = "interaction_vectors"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )
    DB_URL: str
    QDRANT_URL: str
    QDRANT_API_KEY: str
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    LOG_LEVEL: str
    MAX_CONCURRENT_LLM_CALLS: int
    LLM_RETRY_ATTEMPTS: int
    LLM_RETRY_BACKOFF_FACTOR: int
    AWS_REGION: str
    AWS_SECRETS_MANAGER_NAME: str
    TIMEZONE: str = "Europe/Athens"


settings = Settings()

# print(settings)
