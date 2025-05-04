import gzip
from collections.abc import AsyncGenerator
from io import BytesIO

from thesis.injections import authorize, get_session, scoped
from thesis.schemas.generated.quota_pb2 import UploadUserAppRequest, UploadUserAppResponse
from thesis.schemas.generated.quota_pb2_grpc import QuotaServiceServicer


class QuotaServicer(QuotaServiceServicer):
    @scoped([get_session, authorize])
    async def UploadUserApp(self, stream: AsyncGenerator[UploadUserAppRequest], context, **kwargs):
        buffer = BytesIO()
        async for data in stream:
            buffer.write(data.chunk)

        gzip.decompress(buffer)
        return UploadUserAppResponse(resource_id="1")
