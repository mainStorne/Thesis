import grpc

from src.injections.auth_injection import auth_repository
from src.injections.base import scoped
from src.injections.session_injection import database
from src.repositories.auth_repository import AuthRepository, UserNotFoundException
from src.schemas.generated.quota_pb2 import AccountRequest, CreateUserRequest, CreateUserResponse, LoginUserResponse
from src.schemas.generated.quota_pb2_grpc import AuthorizationServicer as _AuthorizationServicer
from src.services.quota_service import CreateUserException


class AuthorizationServicer(_AuthorizationServicer):
    @scoped([database.get_session, auth_repository])
    async def LoginUser(
        self,
        request: AccountRequest,
        context: grpc.aio.ServicerContext,
        auth_repository: AuthRepository,
        **kwargs,
    ):
        try:
            token = await auth_repository.login_user(request.login, request.password)
        except UserNotFoundException:
            return await context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        return LoginUserResponse(token=token)

    # TODO create schema validation from pydantic
    @scoped([database.get_session, auth_repository])
    async def CreateUser(
        self,
        request: CreateUserRequest,
        context: grpc.aio.ServicerContext,
        auth_repository: AuthRepository,
        **kwargs,
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
            user_id, token = await auth_repository.create_user(user_id)
        except CreateUserException:
            return await context.abort(grpc.StatusCode.INTERNAL, "User creation failed")

        return CreateUserResponse(user_id=str(user_id), token=token)
