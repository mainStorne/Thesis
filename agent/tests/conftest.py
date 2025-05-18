from src.init import initialize
import pytest


@pytest.fixture(autouse=True)
async def init():
    await initialize()
