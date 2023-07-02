import os
import dotenv
from pydantic.dataclasses import dataclass

dotenv.load_dotenv()


@dataclass
class Config:
    DB_USER: str = os.environ.get("DB_USER", "postgres")
    DB_PASSWD: str = os.environ.get("DB_PASSWD", "postgres")
    DB_HOST: str = os.environ.get("DB_HOST", "localhost")
    DB_PORT: str = os.environ.get("DB_PORT", "5432")
    DB_NAME: str = os.environ.get("DB_NAME", "stock")
    DB_URL: str = (
        f"postgresql://{DB_USER}:{DB_PASSWD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    MLFLOW_URI: str = os.environ.get("MLFLOW_URI")
