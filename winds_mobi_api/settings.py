from pydantic import BaseSettings


class Settings(BaseSettings):
    port: int = 8000
    environment: str = "local"
    mongodb_url: str
    openapi_prefix: str = ""
    doc_path: str = "doc"
    sentry_dsn: str = None


settings = Settings()
