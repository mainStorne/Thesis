from uuid import UUID

from sqlmodel import select


class QuotaService:
    async def get_user_limits(self, user_id: UUID):
        select()


quota_service = QuotaService()
