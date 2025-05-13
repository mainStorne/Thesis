from contextlib import AsyncExitStack
from typing import AsyncContextManager  # noqa: UP035


def scoped(async_managers: list[AsyncContextManager]):
    def wrapped(func):
        # args saves (self, request, context)
        async def wrapper(*args, **kwargs):
            state = kwargs
            state["context"] = args[2]
            state["request"] = args[1]
            async with AsyncExitStack() as stack:
                for manager in async_managers:
                    await stack.enter_async_context(manager(state))

                return await func(args[0], **state)

        return wrapper

    return wrapped
