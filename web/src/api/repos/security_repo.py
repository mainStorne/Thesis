from abc import ABC, abstractmethod
from uuid import UUID

import jwt
from pydantic import BaseModel, ValidationError

from src.api.repos.base import RepoError
from src.conf import app_settings


class SecurityException(RepoError):
    pass


class DecodeException(SecurityException):
    pass


class Payload(BaseModel):
    id: UUID


class TokenIsMissing(SecurityException):
    pass


class ISecurityRepo(ABC):
    def __init__(self, jwt_secret: str, algorithm: str):
        self._jwt_secret = jwt_secret
        self._algorithm = algorithm
        self._header_name = "authorization"

    @abstractmethod
    def encode(self, payload: Payload) -> str: ...

    @abstractmethod
    def decode(self, token: str) -> Payload:
        """
        raises: DecodeException
        """
        pass


class JwtSecurityRepo(ISecurityRepo):
    def encode(self, payload: dict):
        return jwt.encode(payload, key=self._jwt_secret, algorithm=self._algorithm)

    def decode(self, token: str):
        try:
            return Payload(**jwt.decode(token, self._jwt_secret, algorithms=[self._algorithm]))
        except jwt.exceptions.PyJWTError as e:
            raise DecodeException from e
        except ValidationError as e:
            raise DecodeException from e

    def validate(self, dict_: dict) -> str:
        try:
            token: str = dict_[self._header_name]
            schema, _, value = token.partition(" ")
            if not value or schema.lower() != "bearer":
                raise TokenIsMissing
        except KeyError:
            raise TokenIsMissing  # noqa: B904
        else:
            return value


security_repo = JwtSecurityRepo(app_settings.jwt_secret, "HS256")
