import asyncio
from collections.abc import Callable

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import clear_mappers

from adapters.orm import mapper_registry, start_mappers
from config import settings


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def database_engine():
    return create_async_engine(
        settings.DATABASE_URL,
        connect_args={"server_settings": {"application_name": "test_application"}},
    )


@pytest.fixture
async def initialize_database(database_engine: AsyncEngine):
    async with database_engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)
        await conn.run_sync(mapper_registry.metadata.create_all)
    return database_engine


@pytest.fixture
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


@pytest.fixture
async def session(database_session_factory: AsyncSessionFactory):
    async with database_session_factory() as session:
        yield session


@pytest.fixture
async def add_stock(session: AsyncSession):
    batches_added = set()
    skus_added = set()

    async def _add_stock(lines):
        for ref, sku, qty, eta in lines:
            await session.execute(
                text("INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES (:ref, :sku, :qty, :eta)"),
                {"ref": ref, "sku": sku, "qty": qty, "eta": eta},
            )
            [[batch_id]] = await session.execute(
                text("SELECT id FROM batches WHERE reference=:ref AND sku=:sku"),
                {"ref": ref, "sku": sku},
            )
            batches_added.add(batch_id)
            skus_added.add(sku)
        await session.commit()

    yield _add_stock

    for batch_id in batches_added:
        await session.execute(
            text("DELETE FROM allocations WHERE batch_id=:batch_id"),
            {"batch_id": batch_id},
        )
        await session.execute(
            text("DELETE FROM batches WHERE id=:batch_id"),
            {"batch_id": batch_id},
        )
    for sku in skus_added:
        await session.execute(
            text("DELETE FROM order_lines WHERE sku=:sku"),
            {"sku": sku},
        )
        await session.commit()


@pytest.fixture
async def init_app():
    from entrypoints.fastapi_app import app

    async with LifespanManager(app) as manager:
        yield manager.app


@pytest.fixture
async def api_client(init_app):
    async with AsyncClient(app=init_app, base_url=settings.API_URL) as client:
        yield client
