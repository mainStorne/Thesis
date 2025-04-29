from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="postgres_")
    user: str
    password: str
    host: str
    port: int
    db: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
