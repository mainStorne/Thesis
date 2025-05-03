from typing import ClassVar as _ClassVar
from typing import Optional as _Optional

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message

DESCRIPTOR: _descriptor.FileDescriptor

class CreateUserRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class CreateUserResponse(_message.Message):
    __slots__ = ("quota_limit",)
    QUOTA_LIMIT_FIELD_NUMBER: _ClassVar[int]
    quota_limit: str
    def __init__(self, quota_limit: _Optional[str] = ...) -> None: ...
