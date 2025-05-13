import asyncio
import shutil
import tarfile
import tempfile
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile


class IArchiveRepo(ABC):
    @abstractmethod
    async def create_tar(self, path: Path, buffer: BytesIO, username: str, groupname: str):
        pass


class ArchiveRepo(IArchiveRepo):

    async def create_tar(self, path, buffer, username: str, groupname: str):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, self._create_tar, path, buffer, username, groupname)

    def _save_file(self, buffer: BytesIO, path: str, username: str, groupname: str):
        file = open(path, mode='wb+')
        file.write(buffer.getvalue())
        file.seek(0)
        try:
            shutil.chown(path, username, groupname)
        except Exception:
            shutil.rmtree(path, True)
            raise
        return file

    def _create_tar(self, path: Path, buffer: BytesIO, username: str, groupname: str):
        dockerfile = """FROM traefik/whoami
"""

        dockerfile = BytesIO(dockerfile.encode())

        file = self._save_file(buffer, path, username, groupname)
        with tempfile.TemporaryDirectory() as tempdir:
            with ZipFile(file) as zipped:
                zipped.extractall(tempdir)  # noqa: S202

            f = tempfile.NamedTemporaryFile()  # noqa: SIM115
            t = tarfile.open(mode="w:gz", fileobj=f)  # noqa: SIM115
            t.add(tempdir)

        file.close()

        dfinfo = tarfile.TarInfo("Dockerfile")
        dfinfo.size = len(dockerfile.getvalue())
        dockerfile.seek(0)
        t.addfile(dfinfo, dockerfile)
        t.close()
        f.seek(0)
        return f
