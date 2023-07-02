from pydantic import BaseModel
from datetime import date


class StockData(BaseModel):
    Ticker: str
    Date: date
    Open: int
    High: int
    Low: int
    Close: int
    Volume: int
    Value: int
    Change: float
