from app.common.config import Config
from dataclasses import asdict
import mlflow

conf_dict = asdict(Config())
mlflow.set_tracking_uri(conf_dict["MLFLOW_URI"])


def load_model(name: str):
    model = mlflow.sklearn.load_model(f"models:/{name}/latest")
    return model
