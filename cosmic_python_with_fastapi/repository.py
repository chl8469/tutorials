from typing import Protocol


import model


class RepositoryProtocol(Protocol):
    def add(self, batch: model.Batch) -> None: ...

    def get(self, reference: str) -> model.Batch: ...

