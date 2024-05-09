import asyncio
from collections.abc import Callable

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import clear_mappers

from config import settings
from orm import mapper_registry, start_mappers


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def database_engine():
    return create_async_engine(settings.DATABASE_URL)


@pytest.fixture()
async def initialize_database(database_engine: AsyncEngine):
    async with database_engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)
        await conn.run_sync(mapper_registry.metadata.create_all)
    return database_engine


@pytest.fixture()
def _orm_mapping():
    start_mappers()
    yield
    clear_mappers()


AsyncSessionFactory = Callable[[], AsyncSession]


@pytest.fixture(scope="session")
def database_session_factory(
    database_engine: AsyncEngine,
) -> AsyncSessionFactory:
    return async_sessionmaker(
        bind=database_engine,
        autocommit=False,
        autoflush=False,
    )


@pytest.fixture()
async def session(database_session_factory: AsyncSessionFactory):
    async with database_session_factory() as session:
        yield session
