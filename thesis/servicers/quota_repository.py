from uuid import UUID

from .quota_service import QuotaService


class UserNotFoundException(Exception):
    pass


class UserIDValidationError(Exception):
    def __repr__(self):
        return "Argument user_id is wrong"


class QuotaRepository:
    def __init__(self, quota_service: QuotaService):
        self._quota_service = quota_service

    async def create_user(self, user_id: UUID):
        user = await self._quota_service.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException
        await self._quota_service.create_user(user)
