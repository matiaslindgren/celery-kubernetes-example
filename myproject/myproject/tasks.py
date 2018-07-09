"""
Celery task wrappers for lcs.longest_common_substr.
Tasks will be routed to 2 different queues depending on input size.

Celery workers deployed remotely on Kubernetes will consume tasks from the large_tasks queue,
while local workers consume from the small_tasks queue.
"""
import celery
from lcs.tasks import longest_common_substr
from django.conf import settings
from myproject.models import Task

logger = celery.utils.log.get_task_logger(__name__)


@celery.shared_task(ignore_result=True)
def queue_lcs(task_id):
    """
    Queue existing task with given id for execution.
    """
    task = Task.objects.get(pk=task_id)
    logger.info("Queing task %s", task)
    str_a, str_b = task.string_a, task.string_b

    # Choose task depending on input size
    if max(len(str_a), len(str_b)) > settings.MAX_INPUT_SIZE:
        # Too large input, route to remote task queue
        routed_task = longest_common_substr.signature(
            (str_a, str_b),
            immutable=True,
            options={"queue": "large_tasks"}
        )
        logger.info("Too large input, routing to remote consumer")
    else:
        # Sufficiently small input, route to local task queue
        routed_task = longest_common_substr.signature(
            (str_a, str_b),
            immutable=True,
            options={"queue": "small_tasks"}
        )
        logger.info("Small input, routing to local consumer")

    # Queue task and write its result to database when ready
    celery.chain(routed_task, write_result.s(task_id))()
    # celery.chain does not block this task
    logger.info("Task %s queued", task)


@celery.shared_task(ignore_result=True)
def write_result(result, task_id):
    """
    Write result of a task into the database.
    """
    task = Task.objects.get(pk=task_id)
    task.lcs = result
    task.save()

