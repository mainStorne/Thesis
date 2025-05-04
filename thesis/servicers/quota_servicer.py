from thesis.schemas.generated.quota_pb2 import UploadUserAppRequest
from thesis.schemas.generated.quota_pb2_grpc import QuotaServiceServicer


class QuotaServicer(QuotaServiceServicer):
    async def UploadUserApp(self, request: UploadUserAppRequest, context):
        return super().UploadUserApp(request, context)
