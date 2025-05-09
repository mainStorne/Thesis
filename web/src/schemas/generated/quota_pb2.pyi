from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AccountRequest(_message.Message):
    __slots__ = ("login", "password")
    LOGIN_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    login: str
    password: str
    def __init__(self, login: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class LoginUserResponse(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class CreateUserRequest(_message.Message):
    __slots__ = ("student", "teacher")
    class Profile(_message.Message):
        __slots__ = ("first_name", "middle_name", "last_name", "account")
        FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
        MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
        LAST_NAME_FIELD_NUMBER: _ClassVar[int]
        ACCOUNT_FIELD_NUMBER: _ClassVar[int]
        first_name: str
        middle_name: str
        last_name: str
        account: AccountRequest
        def __init__(self, first_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., last_name: _Optional[str] = ..., account: _Optional[_Union[AccountRequest, _Mapping]] = ...) -> None: ...
    class Student(_message.Message):
        __slots__ = ("profile", "group_id", "resource_limit")
        PROFILE_FIELD_NUMBER: _ClassVar[int]
        GROUP_ID_FIELD_NUMBER: _ClassVar[int]
        RESOURCE_LIMIT_FIELD_NUMBER: _ClassVar[int]
        profile: CreateUserRequest.Profile
        group_id: str
        resource_limit: str
        def __init__(self, profile: _Optional[_Union[CreateUserRequest.Profile, _Mapping]] = ..., group_id: _Optional[str] = ..., resource_limit: _Optional[str] = ...) -> None: ...
    class Teacher(_message.Message):
        __slots__ = ("profile",)
        PROFILE_FIELD_NUMBER: _ClassVar[int]
        profile: CreateUserRequest.Profile
        def __init__(self, profile: _Optional[_Union[CreateUserRequest.Profile, _Mapping]] = ...) -> None: ...
    STUDENT_FIELD_NUMBER: _ClassVar[int]
    TEACHER_FIELD_NUMBER: _ClassVar[int]
    student: CreateUserRequest.Student
    teacher: CreateUserRequest.Teacher
    def __init__(self, student: _Optional[_Union[CreateUserRequest.Student, _Mapping]] = ..., teacher: _Optional[_Union[CreateUserRequest.Teacher, _Mapping]] = ...) -> None: ...

class StartContainerRequest(_message.Message):
    __slots__ = ("container_id",)
    CONTAINER_ID_FIELD_NUMBER: _ClassVar[int]
    container_id: str
    def __init__(self, container_id: _Optional[str] = ...) -> None: ...

class StartContainerResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UploadUserAppRequest(_message.Message):
    __slots__ = ("chunk",)
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    chunk: bytes
    def __init__(self, chunk: _Optional[bytes] = ...) -> None: ...

class UploadUserAppResponse(_message.Message):
    __slots__ = ("resource_id",)
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    resource_id: str
    def __init__(self, resource_id: _Optional[str] = ...) -> None: ...

class CreateUserResponse(_message.Message):
    __slots__ = ("user_id", "token")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    token: str
    def __init__(self, user_id: _Optional[str] = ..., token: _Optional[str] = ...) -> None: ...
