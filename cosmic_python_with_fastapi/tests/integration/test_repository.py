from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
import pytest

from domain import model
from adapters import repository
from adapters.repository import RepositoryProtocol

pytestmark = pytest.mark.usefixtures("_orm_mapping", "initialize_database")


async def test_repository_can_save_a_batch(session: AsyncSession):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo: RepositoryProtocol = repository.SqlAlchemyRepository(session)
    repo.add(batch)
    await session.commit()

    rows = await session.execute(text("SELECT reference, sku, _purchased_quantity, eta FROM batches"))
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


async def insert_order_line(session: AsyncSession):
    await session.execute(text("INSERT INTO order_lines (orderid, sku, qty) VALUES ('order1', 'GENERIC-SOFA', 12)"))
    [[orderline_id]] = await session.execute(
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid="order1", sku="GENERIC-SOFA"),
    )
    return orderline_id


async def insert_batch(session: AsyncSession, batch_id):
    await session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
            " VALUES (:batch_id, 'GENERIC-SOFA', 100, null)"
        ),
        dict(batch_id=batch_id),
    )
    [[batch_id]] = await session.execute(
        text("SELECT id FROM batches WHERE reference=:batch_id AND sku='GENERIC-SOFA'"),
        dict(batch_id=batch_id),
    )
    return batch_id


async def insert_allocation(session: AsyncSession, orderline_id, batch_id):
    await session.execute(
        text("INSERT INTO allocations (orderline_id, batch_id) VALUES (:orderline_id, :batch_id)"),
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


async def test_repository_can_retrieve_a_batch_with_allocations(session: AsyncSession):
    orderline_id = await insert_order_line(session)
    batch1_id = await insert_batch(session, "batch1")
    await insert_batch(session, "batch2")
    await insert_allocation(session, orderline_id, batch1_id)

    repo: RepositoryProtocol = repository.SqlAlchemyRepository(session)
    retrieved: model.Batch = await repo.get("batch1")

    expected = model.Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        model.OrderLine("order1", "GENERIC-SOFA", 12),
    }


async def test_repository_can_retrieve_allocations(session: AsyncSession):
    orderline_id = await insert_order_line(session)
    batch1_id = await insert_batch(session, "batch1")
    await insert_batch(session, "batch2")
    await insert_allocation(session, orderline_id, batch1_id)

    repo: RepositoryProtocol = repository.SqlAlchemyRepository(session)
    retrieved: model.Batch = await repo.get("batch1")

    assert retrieved._allocations == {
        model.OrderLine("order1", "GENERIC-SOFA", 12),
    }
    retrieved: model.Batch = await repo.get("batch2")
    assert retrieved._allocations == set()

    with pytest.raises(NoResultFound):
        await repo.get("batch3")
