from config import Config
from dataclasses import asdict
from sqlalchemy import create_engine
import pandas as pd


config = asdict(Config())
engine = create_engine(config["DB_URL"])

types = {
    "Ticker": str,
    "Date": str,
    "Open": int,
    "High": int,
    "Low": int,
    "Close": int,
    "Volume": int,
    "Value": int,
    "Change": float
}

df = pd.read_csv("stock_data.csv", dtype=types)
df["Date"] = pd.to_datetime(df["Date"])
df.to_sql("stock", engine, if_exists="append", index=False)