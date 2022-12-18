from flow import stock_data
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule


deployment = Deployment.build_from_flow(
    flow=stock_data,
    name="stock-data-pipeline",
    parameters={"ticker": "005930"},
    infra_overrides={"env": {"PREFECT_LOGGING_LEVEL": "DEBUG"}},
    work_queue_name="instance1",
    schedule=(CronSchedule(cron="0 0 * * *", timezone="Asia/Seoul")),
)

if __name__ == "__main__":
    deployment.apply()
