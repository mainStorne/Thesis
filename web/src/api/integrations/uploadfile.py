from fastapi import APIRouter, HTTPException, UploadFile, status

from grpc.aio import AioRpcError
from src.api.deps import AuthorizeDependency
from src.grpc.quota_pb2 import GetUserQuotaRequest, UploadUserAppRequest
from src.grpc.quota_pb2_grpc import QuotaServiceStub
from src.grpc_connection import grpc_connection

r = APIRouter()


@r.put("/upload", status_code=204)
async def flet_uploads(uploadfile: UploadFile, token: str, name: str, auth: AuthorizeDependency):
    # maybe check for size limit
    # check on file extension and so on
    if not uploadfile.size:
        raise HTTPException(status_code=422, detail='File without size')

    account, _ = auth
    quota_stub = None
    for channel in grpc_connection.channels:
        stub = QuotaServiceStub(channel)
        try:
            response = await stub.GetUserQuota(GetUserQuotaRequest(username=account.login))
        except AioRpcError:
            # maybe release channel from pool
            continue

        if response.available_space < uploadfile.size:
            continue

        quota_stub = stub
        break
    if not quota_stub:
        raise HTTPException(status_code=422, detail='Small space available')

    async def _write_to_grpc_stream():
        async for chunk in uploadfile.read():
            yield UploadUserAppRequest(chunk=chunk)
    try:
        response = await quota_stub.UploadUserApp(_write_to_grpc_stream(),
                                                  metadata=(
            ('filename', name),
        ))
    except AioRpcError as e:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.details())
