from abc import ABC, abstractmethod
from uuid import UUID

import jwt
from pydantic import BaseModel, ValidationError

from thesis.db.users import Account


class SecurityException:
    pass


class DecodeException(SecurityException):
    pass


class Payload(BaseModel):
    id: UUID


class ISecurityService(ABC):
    def __init__(self, jwt_secret: str, algorithm: str):
        self._jwt_secret = jwt_secret
        self._algorithm = algorithm

    @abstractmethod
    def encode(self, payload: Payload) -> str: ...

    @abstractmethod
    def decode(self, token: str) -> Payload:
        """
        raises: DecodeException
        """
        pass

    @abstractmethod
    def generate_token(self, account: Account):
        pass


class JwtSecurityService(ISecurityService):
    def encode(self, payload: dict):
        return jwt.encode(payload, key=self._jwt_secret, algorithm=self._algorithm)

    def decode(self, token: str):
        try:
            return Payload(**jwt.decode(token, self._jwt_secret, algorithms=[self._algorithm]))
        except jwt.exceptions.PyJWTError:
            raise DecodeException  # noqa: B904
        except ValidationError:
            raise DecodeException  # noqa: B904

    def generate_token(self, account: Account):
        return self.encode({"id": str(account.id)})
