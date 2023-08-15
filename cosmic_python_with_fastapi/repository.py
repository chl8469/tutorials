import abc

import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, batch: model.Batch):
        pass

    @abc.abstractmethod
    async def get(self, reference) -> model.Batch:
        pass
