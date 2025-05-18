from pydantic import RootModel, field_validator  # noqa: A005


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
