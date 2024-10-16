from sqlalchemy.ext.asyncio import AsyncSession

from adapters.repository import RepositoryProtocol
from domain import model


class InvalidSkuError(Exception):
    pass


def is_valid_sku(sku: str, batches: list[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


async def allocate(line: model.OrderLine, repo: RepositoryProtocol, session: AsyncSession) -> str:
    batches = await repo.list()
    if not is_valid_sku(line.sku, batches):
        msg = f"Invalid sku {line.sku}"
        raise InvalidSkuError(msg)

    batchref = model.allocate(line, batches)
    await session.commit()
    return batchref
