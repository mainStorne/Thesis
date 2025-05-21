from uuid import UUID


def is_uuid(value: str):
    try:
        return UUID(value)
    except ValueError:
        return
