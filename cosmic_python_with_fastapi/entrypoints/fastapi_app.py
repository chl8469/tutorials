from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import clear_mappers
from starlette import status

import config
from adapters import repository
from adapters.orm import start_mappers
from domain import model
from service_layer import services


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    start_mappers()
    yield
    clear_mappers()


session_factory = async_sessionmaker(bind=config.engine)


async def get_session():
    async with session_factory() as session:
        yield session


app = FastAPI(lifespan=lifespan)


class AllocateRequest(BaseModel):
    orderid: str
    sku: str
    qty: int


@app.router.post("/allocate", status_code=status.HTTP_201_CREATED)
async def allocate_endpoint(allocation: AllocateRequest, session: Annotated[AsyncSession, Depends(get_session)]):
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(allocation.orderid, allocation.sku, allocation.qty)

    try:
        batchref = await services.allocate(line, repo, session)
    except (model.OutOfStockError, services.InvalidSkuError) as e:
        return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(content={"batchref": batchref}, status_code=status.HTTP_201_CREATED)
