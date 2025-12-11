from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pdf_max_bytes: int = 25 * 1024 * 1024  # 25 MB
    http_timeout_seconds: int = 30

    class Config:
        env_prefix = "PDF_EXTRACT_"


settings = Settings()



