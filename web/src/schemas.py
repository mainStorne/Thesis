from string import ascii_letters

from pydantic import RootModel, field_validator


class ResourceLimit(RootModel):
    root: str

    @field_validator('root')
    @classmethod
    def validate_limit(cls, v: str) -> str:
        if v[-1] not in ["K", "M", "G"]:
            raise ValueError
        if not v[:-1].isdigit():
            raise ValueError
        return v


class DomainLikeName(RootModel):
    root: str

    @field_validator('root')
    @classmethod
    def validate_domainlike(cls, v: str) -> str:
        for char in v:
            if char not in ascii_letters:
                raise ValueError

        return v
