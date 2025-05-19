
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


class SwarmSettings(BaseModel):
    overlay_network_name: str


class MysqlSettings(BaseModel):
    host: str = 'mysql'
    password: str


class AppSettings(YamlBaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=Path(__file__).parent / 'settings.yml')
    jwt_secret: str = "secret"
    swarm: SwarmSettings
    mysql: MysqlSettings
    domain: str
    database: DatabaseSettings


app_settings = AppSettings()
