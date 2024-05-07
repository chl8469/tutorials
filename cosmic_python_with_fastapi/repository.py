from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import model


class RepositoryProtocol(Protocol):
    def add(self, batch: model.Batch) -> None: ...

    def get(self, reference: str) -> model.Batch: ...


class SqlAlchemyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, batch: model.Batch) -> None:
        self.session.add(batch)

    async def get(self, reference: str) -> model.Batch:
        stmt = select(model.Batch).where(model.Batch.reference == reference)
        result = await self.session.execute(stmt)
        return result.unique().scalars().one()
