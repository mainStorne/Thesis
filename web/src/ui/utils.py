from uuid import UUID


def is_uuid(value: str):
    try:
        return UUID(value)
    except ValueError:
        return


def from_string_to_bytes(value: str) -> int:

    if value.endswith('M'):
        count = int(value[:-1])
        return count * 1048576
