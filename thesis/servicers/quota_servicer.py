import grpc

from thesis.injections.quota_injection import quota_inject
from thesis.repositories.quota_repository import QuotaRepository, UserNotFoundException
from thesis.schemas.generated.quota_pb2 import AccountRequest, CreateUserRequest, CreateUserResponse, LoginUserResponse
from thesis.schemas.generated.quota_pb2_grpc import QuotaServiceServicer
from thesis.services.quota_service import CreateUserException


class QuotaServicer(QuotaServiceServicer):
    @quota_inject
    async def LoginUser(
        self,
        request: AccountRequest,
        context: grpc.aio.ServicerContext,
        quota_repository: QuotaRepository,
    ):
        try:
            token = await quota_repository.login_user(request.login, request.password)
        except UserNotFoundException:
            return await context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        return LoginUserResponse(token=token)

    # TODO create wrapped and propagate quota_repository
    @quota_inject
    async def CreateUser(
        self,
        request: CreateUserRequest,
        context: grpc.aio.ServicerContext,
        quota_repository: QuotaRepository,
    ):
        field = request.WhichOneof("user_profile")
        if field is None:
            pass
        user: CreateUserRequest.Student = getattr(request, field)
        if user.resource_limit[-2:] not in ["K", "M", "G"]:
            pass
        if not user.resource_limit[:-2].isdigit():
            pass

        try:
            user = await quota_repository.create_user(user)
        except CreateUserException:
            return await context.abort(grpc.StatusCode.INTERNAL, "User creation failed")

        return CreateUserResponse(user_id=str(user.id))
