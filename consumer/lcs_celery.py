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
    address = os.environ["BROKER_ADDRESS"]
    broker_address = f"amqp://{user}:{password}@{address}"
    return Celery("lcs_celery", broker=broker_address)

app = make_celery()

if __name__ == "__main__":
    # Make this celery app executable from the command line
    app.worker_main()
