from collections.abc import AsyncGenerator
from io import BytesIO

from structlog import get_logger

from grpc import StatusCode
from src.conf import settings
from src.grpc.quota_pb2 import UploadUserAppRequest, UploadUserAppResponse
from src.grpc.quota_pb2_grpc import QuotaServiceServicer
from src.injections import authorize, get_session, scoped
from src.services.quota_service import ArchiveError, QuotaExcitedError, QuotaService, get_quota_service

log = get_logger()


class QuotaServicer(QuotaServiceServicer):
    @scoped([get_session, authorize, get_quota_service])
    async def UploadUserApp(self, request: AsyncGenerator[UploadUserAppRequest], context, quota_service: QuotaService, **state):
        metadata = state['metadata']
        filename = metadata['filename']
        if not filename:
            return await context.abort(StatusCode.INTERNAL, 'Filename didnt provided')

        buffer = BytesIO()
        size = 0
        async for data in request:
            size += len(data.chunk)
            if size > settings.max_file_size_in_bytes:
                return await context.abort(StatusCode.CANCELLED, f'File size is more then {settings.max_file_size_in_bytes}')
            buffer.write(data.chunk)
        buffer.seek(0)
        try:
            await quota_service.upload_user_app(buffer, size, filename)
        except QuotaExcitedError as e:
            await log.aexception('Error getting guota', exc_info=e)
            return await context.abort(StatusCode.INTERNAL, 'Quota filled')
        except ArchiveError as e:
            await log.aexception('Error getting guota', exc_info=e)
            return await context.abort(StatusCode.INTERNAL, 'Archive error')
        else:
            return UploadUserAppResponse(resource_id='1')
