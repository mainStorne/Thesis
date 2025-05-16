from uuid import uuid4

import structlog
from grpc_interceptor import AsyncServerInterceptor
from structlog import get_logger
from structlog.stdlib import BoundLogger

import grpc
from grpc.aio import AioRpcError

log: BoundLogger = get_logger()


class LoggingInterceptor(AsyncServerInterceptor):
    async def intercept(self, method, request_or_iterator, context: grpc.aio.ServicerContext, method_name):
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=str(uuid4()))
        await log.ainfo("Request")
        try:
            response = await method(request_or_iterator, context)
        except AioRpcError as e:
            await log.awarning("AioRpcError", exc_info=e)
            raise
        except Exception as e:
            await log.aexception("Exception in request handler", exc_info=e)
            await context.abort(grpc.StatusCode.INTERNAL, "Unknown exception")
            return

        await log.ainfo("Response")
        return response
