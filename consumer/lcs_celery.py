"""
Celery app that wraps calls to an external Python library 'lcs' into asynchronous tasks.
"""
import os
from celery import Celery
# Celery sniffs task definitions from imports
from lcs.tasks import longest_common_substr

def make_celery():
    # We let the Kubernetes controller handle RabbitMQ configuration.
    # Notice, though, that RabbitMQ is not deployed in the Kubernetes cluster.
    user = os.environ["BROKER_USER"]
    password = os.environ["BROKER_PASSWORD"]
    url = os.environ["BROKER_URL"]
    broker_url = f"amqp://{user}:{password}@{url}"
    return Celery("lcs_celery", broker=broker_url)

if __name__ == "__main__":
    app = make_celery()
    # Make this celery app executable from the command line
    app.worker_main()
