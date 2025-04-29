import pytest
from api import app
from api.conf import engine
from api.deps import get_session
from httpx import ASGITransport, AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

pytestmark = pytest.mark.anyio


@pytest.fixture()
async def client():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as cli:
        yield cli


@pytest.fixture()
async def connection():
    async with engine.connect() as conn:
        yield conn


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def transaction(connection):
    async with connection.begin() as trans:
        yield trans


@pytest.fixture(autouse=True)
async def session(connection, transaction):
    async_session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )
    async with async_session as session:

        async def inner():
            return session

        app.dependency_overrides[get_session] = inner
        yield session

    await transaction.rollback()
