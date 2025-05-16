import grpc
from src.grpc.quota_pb2 import (
    AccountRequest,
    CreateUserRequest,
    CreateUserResponse,
    LoginUserResponse,
)
from src.grpc.quota_pb2_grpc import AuthorizationServicer as _AuthorizationServicer
from src.injections import get_session, scoped
from src.repos.quota_repo import QuotaError
from src.services.auth_service import (
    AuthService,
    UserNotFoundException,
    get_auth_service,
)


class AuthorizationServicer(_AuthorizationServicer):
    @scoped([get_session, get_auth_service])
    async def LoginUser(
        self,
        request: AccountRequest,
        context: grpc.aio.ServicerContext,
        auth_service: AuthService,
        **state,
    ):
        try:
            token = await auth_service.login_user(request.login, request.password)
        except UserNotFoundException:
            return await context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        return LoginUserResponse(token=token)

    # TODO create schema validation from pydantic
    @scoped([get_session, get_auth_service])
    async def CreateUser(
        self,
        request: CreateUserRequest,
        context: grpc.aio.ServicerContext,
        auth_service: AuthService,
        **state,
    ):
        field = request.WhichOneof("user_profile")
        if field is None:
            pass
        user_id: CreateUserRequest.Student = getattr(request, field)
        if user_id.resource_limit[-2:] not in ["K", "M", "G"]:
            pass
        if not user_id.resource_limit[:-2].isdigit():
            pass

        try:
            user_id, token = await auth_service.create_user(user_id)
        except QuotaError:
            return await context.abort(grpc.StatusCode.INTERNAL, "User creation failed")

        return CreateUserResponse(user_id=str(user_id), token=token)
