
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings


class DatabaseSettings(BaseModel):
    user: str
    password: str
    host: str
    port: int
    db: str


class EnvSettings(YamlBaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=Path(__file__).parent / 'settings.yml')
    max_file_size_in_bytes: int
    jwt_secret: str = "secret"
    mysql_root_password: str = "dima"
    agent_service_name: str
    database: DatabaseSettings


settings = EnvSettings()
