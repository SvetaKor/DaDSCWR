from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: PostgresDsn
    jwt_secret: str
    jwt_access_ttl_sec: int = 900
    jwt_refresh_ttl_sec: int = 60 * 60 * 24 * 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
