from prefect import flow, task, get_run_logger
from prefect.orion.schemas.states import Completed, Failed
from datetime import datetime, timedelta
from schema import StockData
from config import Config
from dataclasses import asdict
from sqlalchemy import create_engine
from pykrx import stock
import sys


@task(name="stock data extract")
def extract(ticker):
    logger = get_run_logger()
    logger.info(f"ticker: {ticker}")

    today = datetime.utcnow() + timedelta(hours=9)
    t1 = (today - timedelta(days=2)).strftime("%Y%m%d")
    t2 = (today - timedelta(days=1)).strftime("%Y%m%d")
    logger.info(f"t1: {t1}\nt2: {t2}")

    df = stock.get_market_ohlcv_by_date(t1, t2, ticker)
    df["Ticker"] = ticker
    return df


@task(name="stock data transform")
def transform(df):
    logger = get_run_logger()
    cols = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Value",
        "Change",
        "Ticker"
        ]

    df = df.reset_index()
    if len(cols) != len(df.columns):
        logger.error(df.columns)
        return "Fail"

    df.columns = cols
    try:
        StockData(**df.loc[0])
    except Exception as e:
        logger.error(e)
        return "Fail"
    return df


@task(name="load to database")
def load(df):
    logger = get_run_logger()

    config = asdict(Config())
    engine = create_engine(config["DB_URL"])
    try:
        df.to_sql("stock", engine, if_exists="append", index=False)
    except Exception as e:
        logger.error(e)
        return "Fail"


@flow(name="stock_data_etl")
def stock_data(ticker):
    logger = get_run_logger()
    logger.info("start ETL pipeline")

    df = extract(ticker)
    if df.shape[0] == 0:
        logger.error(df)
        return Completed(message="nothing to update")
    logger.info(f"data shape: {df.shape}")

    df = transform(df)
    if isinstance(df, str) and df == "Fail":
        return Failed(message="failed to transform data")

    result = load(df)
    if result == "Fail":
        return Failed(message="failed to load data")


if __name__=="__main__":
    ticker = sys.argv[1]
    stock_data()
