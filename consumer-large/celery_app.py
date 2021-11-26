"""
CLI Celery app for handling lcs.tasks.longest_common_substr calls asynchronously.
"""
import os
from celery import Celery
from lcs.tasks import longest_common_substr


def make_celery():
    return Celery("consumer-large",
            backend=os.environ.get("CELERY_RESULT_BACKEND"),
            broker=os.environ["CELERY_BROKER_URL"])

if __name__ == "__main__":
    make_celery().worker_main()
