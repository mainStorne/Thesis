
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="postgres_")
    user: str
    password: str
    host: str
    port: int
    db: str


class QuotaSettings(BaseSettings):
    students_shared_base_dir: Path
    students_home_base_dir: Path

    @field_validator('students_home_base_dir', 'students_home_base_dir', mode='after')
    @classmethod
    def add_prefix(cls, value: Path):
        return Path('/fs') / str(value)[1:]


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")
    max_file_size_in_bytes: int
    jwt_secret: str = "secret"
    mysql_root_password: str = "dima"
    quota: QuotaSettings = Field(default_factory=QuotaSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
