from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="postgres_")
    user: str
    password: str
    host: str
    port: int
    db: str


class QuotaSettings(BaseSettings):
    mount_point: str = "/test/filesystem"
    base_home_dir: str = "/test/filesystem/home"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")
    jwt_secret: str = "secret"
    mysql_root_password: str = "dima"
    quota: QuotaSettings = Field(default_factory=QuotaSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
