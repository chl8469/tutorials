from datetime import date
import uuid

from httpx import AsyncClient


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


async def test_happy_path_returns_201_and_allocated_batch(api_client: AsyncClient, add_stock):
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    await add_stock(
        [
            (laterbatch, sku, 100, date(2011, 1, 2)),
            (earlybatch, sku, 100, date(2011, 1, 1)),
            (otherbatch, othersku, 100, None),
        ]
    )
    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}

    r = await api_client.post("/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch


async def test_unhappy_path_returns_400_and_error_message(api_client: AsyncClient):
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}
    r = await api_client.post("/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"
