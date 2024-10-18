import pytest
from domain import model
from service_layer import services


class FakeRepository:
    def __init__(self, batches: list[model.Batch]) -> None:
        self._batches = set(batches)

    def add(self, batch: model.Batch) -> None:
        self._batches.add(batch)

    def get(self, reference: str) -> model.Batch:
        return next(b for b in self._batches if b.reference == reference)

    async def list(self) -> list[model.Batch]:
        return list(self._batches)


class FakeSession:  # 임시 해법이며 6장에서 올바른 해법을 배운다고함
    committed = False

    async def commit(self) -> None:
        self.committed = True


async def test_returns_allocation():
    line = model.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = await services.allocate(line, repo, FakeSession())
    assert result == "b1"


async def test_error_for_invalid_sku():
    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSkuError, match="Invalid sku NONEXISTENTSKU"):
        await services.allocate(line, repo, FakeSession())


async def test_commits():
    line = model.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    await services.allocate(line, repo, session)
    assert session.committed is True
