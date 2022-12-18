from fastapi import APIRouter
from app.schemas.stock import StockTsRecv, StockTsResp
from app.services.stock import predict_stock_ts

router = APIRouter()


@router.post("/close", name="다음날 종가 예측", response_model=StockTsResp)
def stock_prediction(ts:StockTsRecv):
    pred_result = predict_stock_ts(ts.model_name, ts.timeseries)
    return {"closing_price": pred_result}