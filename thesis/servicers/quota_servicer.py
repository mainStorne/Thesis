import grpc
from dependency_injector.wiring import Provide, inject

from ..database import scoped
from ..generated.quota_pb2 import CreateUserRequest, CreateUserResponse
from ..generated.quota_pb2_grpc import QuotaServiceServicer
from .quota_container import QuotaContainer
from .quota_repository import QuotaRepository, UserIDValidationError, UserNotFoundException
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
        quota_limit = "200MB"
        try:
            await quota_repository.create_user(request.user_id)
        except UserIDValidationError as e:
            return await context.abort(grpc.StatusCode.INTERNAL, repr(e))
        except UserNotFoundException:
            return await context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        except CreateUserException:
            return await context.abort(grpc.StatusCode.INTERNAL, "User creation failed")

        return CreateUserResponse(quota_limit=quota_limit)
