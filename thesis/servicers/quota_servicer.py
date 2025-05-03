from uuid import UUID

import grpc
from dependency_injector.wiring import Provide, inject

from ..database import scoped
from ..schemas.generated.quota_pb2 import CreateUserRequest, CreateUserResponse
from ..schemas.generated.quota_pb2_grpc import QuotaServiceServicer
from .quota_container import QuotaContainer
from .quota_repository import QuotaRepository, UserNotFoundException
from .quota_service import CreateUserException


class QuotaServicer(QuotaServiceServicer):
    @inject
    @scoped
    async def CreateUser(
        self,
        request: CreateUserRequest,
        context: grpc.aio.ServicerContext,
        quota_repository: QuotaRepository = Provide[QuotaContainer.quota_repository],
    ):
        try:
            user_id = UUID(request.user_id)
        except ValueError:
            return await context.abort(grpc.StatusCode.INTERNAL, "Argument user_id is wrong")
        quota_limit = "200MB"
        try:
            await quota_repository.create_user(user_id)
        except UserNotFoundException:
            return await context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        except CreateUserException:
            return await context.abort(grpc.StatusCode.INTERNAL, "User creation failed")

        return CreateUserResponse(quota_limit=quota_limit)
