from pydantic import ValidationError

from grpc import StatusCode
from src.grpc.quota_pb2 import CreateSharedResourceRequest, CreateSharedResourceResponse
from src.grpc.quota_pb2_grpc import ResourcesServicer as _ResourcesServicer
from src.repos.filesystem_repo import FileSystemError
from src.repos.quota_repo import QuotaError
from src.schemas import ResourceLimit
from src.services.resources_service import resource_service


class ResourcesServicer(_ResourcesServicer):

    async def CreateSharedResource(self, request: CreateSharedResourceRequest, context):
        try:
            limit = ResourceLimit(request.limit)
        except ValidationError:
            return await context.abort(StatusCode.ABORTED, 'Limit wrong')
        try:
            volume_path, uid, gid = await resource_service.create_shared_resource(limit, username=request.name)
        except FileSystemError:
            return await context.abort(StatusCode.ABORTED, 'User already exists!')
        except QuotaError:
            return await context.abort(StatusCode.ABORTED, 'User quota error!')
        else:
            return CreateSharedResourceResponse(volume_path=volume_path, uid=uid, gid=gid)

    async def UploadStudentResource(self, request_iterator, context):
        return super().UploadStudentResource(request_iterator, context)
