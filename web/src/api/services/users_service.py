from structlog import get_logger

from src.api.db.users import Student

log = get_logger()


class UsersRepo:
    async def create_student(self, session, student: Student):
        student.profile.account.password = self._account_repo.hash_password(student.account.password)
        session.add(student)
        await session.commit()
        # await self._quota_repo.create_student(student)

    # async def create_user(self, user: CreateUserRequest.Student | CreateUserRequest.Teacher):
    #     if isinstance(user, CreateUserRequest.Teacher):
    #         raise
    #     else:
    #         plain_password = user.profile.account.password
    #         login = user.profile.account.login
    #         await self._quota_repo.create_student_to_filesystem(login)

    #         try:
    #             await self._quota_repo.set_quota(login, user.resource_limit)
    #         except QuotaError:
    #             await self._quota_repo.delete_student_from_filesystem(login)
    #             raise

    #         try:
    #             await self._quota_repo.register_student_to_mysql(login, plain_password)
    #         except QuotaError:
    #             await self._quota_repo.delete_student_from_filesystem(login)
    #             raise

    #         try:
    #             student = user
    #             student.profile.account.password = self._account_repo.hash_password(user.profile.account.password)

    #             account = Account(login=student.profile.account.login, hashed_password=student.profile.account.password)
    #             student = Student(
    #                 first_name=student.profile.first_name,
    #                 middle_name=student.profile.middle_name,
    #                 last_name=student.profile.last_name,
    #                 group_id=student.group_id,
    #                 resource_limit=student.resource_limit,
    #             )
    #             student.account = account
    #             login = account.login
    #             await self._quota_repo.create_student(student)
    #         except SQLAlchemyError as e:
    #             await self._quota_repo.delete_student_from_filesystem(login)
    #             await self._quota_repo.unregister_student_from_mysql(login)
    #             raise QuotaError from e
    #         except Exception as e:
    #             await log.aerror("Unexpected error in create_user!", exc_info=e)
    #             await self._quota_repo.delete_student_from_filesystem(login)
    #             await self._quota_repo.unregister_student_from_mysql(login)
    #             raise

    #         return student.id, self._security_repo.generate_token(account)


users_service = UsersRepo()
