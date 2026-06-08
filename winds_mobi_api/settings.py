from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "local"
    port: int = 8000
    mongodb_url: str
    root_path: str
    log_config_path: str | None = str(Path(Path(__file__).parents[0], "logging.yaml"))
    sentry_url: str | None = None
    doc_path: str = "doc"
    response_schema_validation: bool = False


settings = Settings()
