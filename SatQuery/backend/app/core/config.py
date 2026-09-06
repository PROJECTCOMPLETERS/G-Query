from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SatQuery API"
    app_version: str = "0.1.0"
    debug: bool = True
    allowed_origins: str = "*"
    max_upload_size_mb: int = 500

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()