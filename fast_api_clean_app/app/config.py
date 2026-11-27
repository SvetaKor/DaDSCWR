from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: PostgresDsn

    # Password
    jwt_secret: str
    jwt_access_ttl_sec: int = 900
    jwt_refresh_ttl_sec: int = 60 * 60 * 24 * 30

    # Steam
    steam_realm: str = "http://localhost:8000"
    steam_return_url: str = "http://localhost:8000/auth/steam/callback"
    steam_api_key: str = "9FCD0895F2BECF337B0BF4590155AA05"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Frontend
    frontend_url: str = "http://localhost:8000"

settings = Settings()
