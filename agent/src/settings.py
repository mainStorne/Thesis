
from pathlib import Path

from pydantic import BaseModel, field_validator
from pydantic_settings import SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings


class DatabaseSettings(BaseModel):
    user: str
    password: str
    host: str
    port: int
    db: str


class QuotaSettings(BaseModel):
    # model_config = SettingsConfigDict(
    # yaml_file=Path(__file__).parent / 'settings.yml')
    students_shared_base_dir: Path
    students_home_base_dir: Path

    @field_validator('students_home_base_dir', 'students_home_base_dir', mode='after')
    @classmethod
    def add_prefix(cls, value: Path):
        return Path('/fs') / str(value)[1:]


class EnvSettings(YamlBaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=Path(__file__).parent / 'settings.yml')
    max_file_size_in_bytes: int
    jwt_secret: str = "secret"
    mysql_root_password: str = "dima"
    quota: QuotaSettings
    database: DatabaseSettings
