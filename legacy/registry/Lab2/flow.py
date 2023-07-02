from prefect import flow, task, get_run_logger
from prefect.orion.schemas.states import Completed, Failed
from datetime import datetime, timedelta
from schema import StockData
from config import Config
from dataclasses import asdict
from sqlalchemy import create_engine
from pykrx import stock
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from utils import make_dataset
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import io
import mlflow
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


@task(name="experiment")
def ml_pipeline():
    config = asdict(Config())
    engine = create_engine(config["DB_URL"])

    df = pd.read_sql('SELECT * FROM stock ORDER BY "Date"', engine)

    TEST_SIZE = 60
    train = df[:-TEST_SIZE]
    test = df[-TEST_SIZE:]

    feature_cols = ["Close"]
    label_cols = ["Close"]

    train_feature = train[feature_cols]
    train_label = train[label_cols]

    test_feature = test[feature_cols]
    test_label = test[label_cols]

    train_feature, train_label = make_dataset(train_feature, train_label, 20)
    test_feature, test_label = make_dataset(test_feature, test_label, 20)

    model = RandomForestRegressor(max_depth=5, random_state=0)
    model.fit(train_feature.reshape(-1, 20), train_label.flatten())

    train_rsquare = model.score(train_feature.reshape(-1, 20), train_label)
    test_rsquare = model.score(test_feature.reshape(-1, 20), test_label)

    test_pred = model.predict(test_feature.reshape(-1, 20))
    test_label = test_label.flatten()
    test_mse = mean_squared_error(
        test_pred,
        test_label
        )
    params = {
        "train_rsquare": train_rsquare,
        "test_rsquare": test_rsquare,
        "test_mse": test_mse
    }

    expr_name = "project_buffett"
    mlflow.set_tracking_uri(config["MLFLOW_URI"])
    mlflow.set_experiment(expr_name)

    plt.plot(test_label, label="y")
    plt.plot(test_pred, label="pred")
    plt.legend(frameon=False)
    plt.grid(ls="-.")
    plt.title("Closing price")

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    im = Image.open(buffer)

    exp = mlflow.get_experiment_by_name(expr_name)
    exp_id = exp.experiment_id

    mlflow.start_run(experiment_id=exp_id)
    mlflow.log_metrics(params)
    mlflow.log_image(im, "graph/prediction_graph.png")
    mlflow.sklearn.log_model(
        model,
        "stock_sklearn_rf",
        registered_model_name="the_Hand_of_Buffett"
        )
    mlflow.end_run()


@flow(name="stock_data_etl")
def stock_data_ml(ticker):
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

    ml_pipeline()


if __name__=="__main__":
    ticker = sys.argv[1]
    stock_data_ml()
