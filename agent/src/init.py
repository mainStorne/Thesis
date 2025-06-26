import os
from asyncio.subprocess import PIPE, create_subprocess_shell

from structlog import get_logger
from .services.resources_service import resource_service
from .schemas import ResourceLimit

from .conf import app_settings
from .settings import AppEnviromnent

log = get_logger()


async def initialize():
    if app_settings.enviromnent == AppEnviromnent.prod:
        # Use this hack to work in container
        os.chroot("/host")
        os.chdir("/")

    path = app_settings.quota.students_shared_base_dir
    path.mkdir(exist_ok=True)
    students_group = "students"
    process = await create_subprocess_shell(f"groupadd {students_group}", stdout=PIPE, stderr=PIPE)

    _, stderr = await process.communicate()
    if stderr:
        stderr = stderr.decode().strip()
        if stderr != f"groupadd: group '{students_group}' already exists":
            await log.awarning(stderr)
