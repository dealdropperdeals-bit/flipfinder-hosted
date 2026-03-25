from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    cors_origin: str = "http://127.0.0.1:5173"
    jwt_secret: str = "change-me"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
