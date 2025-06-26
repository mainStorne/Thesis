from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings


class QuotaSettings(BaseModel):
    students_shared_base_dir: Path
    students_home_base_dir: Path


class AppEnviromnent(StrEnum):
    local = "LOCAL"
    prod = "PROD"


class AppSettings(YamlBaseSettings):
    model_config = SettingsConfigDict(yaml_file=Path(__file__).parent / "settings.yml")
    quota: QuotaSettings
    enviromnent: AppEnviromnent = AppEnviromnent.prod
