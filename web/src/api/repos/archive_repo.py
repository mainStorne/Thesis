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
    async def create_tar(self, buffer):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, self._create_tar, buffer)

    def _create_tar(self, buffer: BytesIO):
        f = tempfile.NamedTemporaryFile()
        t = tarfile.open(mode="w:gz", fileobj=f)
        with ZipFile(buffer) as zipped:
            for zipinfo in zipped.infolist():

                tarinfo = tarfile.TarInfo()
                tarinfo.name = zipinfo.filename
                tarinfo.size = zipinfo.file_size
                if zipinfo.is_dir():

                    tarinfo.mode = 0o777
                    tarinfo.type = tarfile.DIRTYPE
                else:
                    tarinfo.mode = 0o666
                    tarinfo.type = tarfile.REGTYPE
                infile = zipped.open(zipinfo)
                t.addfile(tarinfo, infile)

        buffer.close()
        t.close()
        f.seek(0)
        return f


archive_repo = ArchiveRepo()
