import model
from sqlalchemy import select, text
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.usefixtures("_orm_mapping", "initialize_database")


async def test_orderline_mapper_can_load_lines(session: AsyncSession):
    insert_order_lines = """
    INSERT INTO order_lines (orderid, sku, qty) VALUES 
    ('order1', 'RED-CHAIR', 12),
    ('order1', 'RED-TABLE', 13),
    ('order2', 'BLUE-LIPSTICK', 14)
    """
    await session.execute(text(insert_order_lines))
    expected = [
        model.OrderLine("order1", "RED-CHAIR", 12),
        model.OrderLine("order1", "RED-TABLE", 13),
        model.OrderLine("order2", "BLUE-LIPSTICK", 14),
    ]
    result = await session.execute(select(model.OrderLine))
    assert result.scalars().all() == expected
