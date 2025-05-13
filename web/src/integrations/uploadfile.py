from fastapi import APIRouter, HTTPException, Request, status

from grpc.aio import AioRpcError
from src.grpc.quota_pb2 import UploadUserAppRequest
from src.grpc_connection import grpc_connection

r = APIRouter()


@r.put("/upload", status_code=204)
async def flet_uploads(request: Request, token: str, name: str):
    stub = grpc_connection.quota_stub

    async def _write_to_grpc_stream():
        size = 0
        async for chunk in request.stream():
            size += len(chunk)
            if 1000 and size > 1000:
                raise HTTPException(  # noqa: TRY003
                    f"Max upload size reached: {1000}"
                )
            yield UploadUserAppRequest(chunk=chunk)
    try:
        response = await stub.UploadUserApp(_write_to_grpc_stream(),
                                            metadata=(
            ('authorization', f'Bearer {token}'),
            ('filename', name),
        ))
    except AioRpcError as e:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.details())
