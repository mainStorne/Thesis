from io import BytesIO
from pathlib import Path
from tarfile import TarFile
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from src.api.repos.archive_repo import archive_repo


async def test_create_tar():
    buffer = BytesIO()
    member = 'test.txt'
    with TemporaryDirectory() as tempdir:
        base_path = Path(tempdir)
        with (base_path / 'test.txt').open('wb') as file:
            file.write(b'helloworld')

        with ZipFile(buffer, "a") as zipped:
            zipped.writestr(member, b'hello-world')
            zipped.write(base_path)
            zipped.write(base_path / 'test.txt')

    buffer.seek(0)
    tar = await archive_repo.create_tar("""FROM traefik/whoami""",  buffer)

    file = TarFile.open(tar.name)
    file.extractfile(member)
    file.extractfile('Dockerfile')
    file.extractfile('.dockerignore')

    file.extractfile(str(base_path)[1:])
    file.extractfile(str(base_path / 'test.txt')[1:])
