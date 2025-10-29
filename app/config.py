# TODO: Import BaseSettings from pydantic_settings
# TODO: Create Settings class with fields: asset_ids, db_path, ingest_interval, log_level
# TODO: Create settings instance

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    asset_ids: str = "bitcoin,ethereum,solana"
    db_path: str = "portfolio.db"
    ingest_interval: int = 300
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()