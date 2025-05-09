from fastapi import APIRouter, Request

from src.grpc.quota_pb2 import UploadUserAppRequest
from src.grpc.quota_pb2_grpc import QuotaServiceStub
from src.grpc_connection import grpc_connection

r = APIRouter()


@r.put("/upload")
async def flet_uploads(request: Request, token: str):
    stub = QuotaServiceStub(grpc_connection.channel)

    async def _write_to_grpc_stream():
        async for chunk in request.stream():
            yield UploadUserAppRequest(chunk=chunk)
    await stub.UploadUserApp(_write_to_grpc_stream(),
                             metadata=(
        ('authorization', f'Bearer {token}'),
    ))
