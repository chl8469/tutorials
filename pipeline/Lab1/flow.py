from prefect import flow, task, get_run_logger
import prefect
import requests
import sys


@task
def log_task(name):
    logger = get_run_logger()
    logger.info("Hello %s!", name)
    logger.info("Prefect Version = %s 🚀", prefect.__version__)


@task(name="requests url")
def request_url(url):
    logger = get_run_logger()
    response = requests.get(url)
    status_code = response.status_code
    if status_code < 400:
        logger.info(status_code)
    else:
        logger.error(status_code)
    return response.text


@flow(name="My_first_pipeline")
def flow_function(name):
    log_task(name)
    result = request_url("https://api.my-ip.io/ip")
    logger = get_run_logger()
    logger.info(result)


if __name__=="__main__":
    name = sys.argv[1]
    flow_function(name)


# prefect deployment build ./flow.py:flow_function -n ip-logging-pipeline -q instance1
# prefect deployment apply flow_function-deployment.yaml
# prefect deployment ls
# prefect deployment run My_first_pipeline/ip-logging-pipeline
# prefect agent start -q 'instance1'
