from pydantic import BaseSettings


class Settings(BaseSettings):
    port: int = 8000
    environment: str = "local"
    sentry_dsn: str = None
    mongodb_url: str
    openapi_prefix: str = ""
    doc_path: str = "doc"
    response_schema_validation: bool = False


settings = Settings()
