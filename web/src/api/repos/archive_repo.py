import asyncio
import tarfile
import tempfile
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from zipfile import ZipFile


class IArchiveRepo(ABC):
    @abstractmethod
    async def create_tar(self, dockerfile: str, buffer: BytesIO):
        pass


class ArchiveRepo(IArchiveRepo):
    async def create_tar(self, dockerfile, buffer):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, self._create_tar, dockerfile, buffer)

    def _create_tar(self, dockerfile: str, buffer: BytesIO):
        dockerfile = BytesIO(dockerfile.encode())

        with tempfile.TemporaryDirectory() as tempdir:
            with ZipFile(buffer) as zipped:
                zipped.extractall(tempdir)  # noqa: S202

            # FIX method of creating tar archive because temp dir also included!
            # now this look like tmp/hash/user-dir, I need to remove /tmp/hash from there
            # and add .dockerignore file to ingore Dockerfile in image!
            f = tempfile.NamedTemporaryFile()  # noqa: SIM115
            t = tarfile.open(mode="w:gz", fileobj=f)  # noqa: SIM115
            t.add(tempdir)

        buffer.close()
        dfinfo = tarfile.TarInfo("Dockerfile")
        dfinfo.size = len(dockerfile.getvalue())
        dockerfile.seek(0)
        t.addfile(dfinfo, dockerfile)
        t.close()
        f.seek(0)
        return f


archive_repo = ArchiveRepo()
