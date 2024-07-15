from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    port: int = 8000
    environment: str = "local"
    sentry_dsn: Optional[str] = None
    mongodb_url: str
    root_path: str = ""
    doc_path: str = "doc"
    response_schema_validation: bool = False


settings = Settings()
