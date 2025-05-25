from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, field_validator
from pydantic_settings import SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings


class QuotaSettings(BaseModel):
    # model_config = SettingsConfigDict(
    # yaml_file=Path(__file__).parent / 'settings.yml')
    students_shared_base_dir: Path
    students_home_base_dir: Path

    @field_validator("students_home_base_dir", "students_home_base_dir", mode="after")
    @classmethod
    def add_prefix(cls, value: Path):
        return Path("/fs") / str(value)[1:]


class AppEnviromnent(StrEnum):
    local = 'LOCAL'
    prod = 'PROD'


class AppSettings(YamlBaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=Path(__file__).parent / "settings.yml")
    quota: QuotaSettings
    enviromnent: AppEnviromnent = AppEnviromnent.prod
