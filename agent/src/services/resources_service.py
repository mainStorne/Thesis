

from pwd import getpwnam

from src.repos.filesystem_repo import FileSystemError, filesystem_repo
from src.repos.quota_repo import quota_repo
from src.schemas import ResourceLimit


class ResourceService:

    async def create_shared_resource(self, limit: ResourceLimit, username: str):
        try:
            await filesystem_repo.create_shared_resource(username)
        except FileSystemError:
            # Delete user if it was a crash or something else and this resource is not started
            await filesystem_repo.delete_user(username)
            await filesystem_repo.create_shared_resource(username)

        await quota_repo.set_quota(username, limit=limit.root)
        entry = getpwnam(username)  # TODO async this
        return f"{filesystem_repo.shared_base_dir}/{username}", entry.pw_uid, entry.pw_gid


resource_service = ResourceService()
