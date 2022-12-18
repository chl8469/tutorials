from pydantic import BaseModel, Field
from typing import List


class StockTsRecv(BaseModel):
    model_name: str = "the_Hand_of_Buffett"
    timeseries: List[int] = Field(..., min_items=20, max_items=20)

    class Config:
        schema_extra = {
            "example":{
            "model_name": "the_Hand_of_Buffett",
            "timeseries": [
                49650,
                49900,
                49400,
                48200,
                47650,
                46600,
                47000,
                47000,
                47050,
                47250,
                46650,
                47000,
                47950,
                46800,
                46650,
                45550,
                46150,
                46250,
                45950,
                44900
                ]
            }
        }


class StockTsResp(BaseModel):
    closing_price: float