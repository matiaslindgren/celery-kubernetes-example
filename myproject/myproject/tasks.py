import celery
import lcs
from django.conf import settings
from myproject.models import Task

@celery.shared_task(ignore_result=True)
def queue_lcs(task_id):
    task = Task.objects.get(pk=task_id)
    if max(len(task.string_a), len(task.string_b)) > settings.MAX_INPUT_SIZE:
        # Too large input, route to remote task queue
        result = "-error too large-"
    else:
        # Sufficiently small input, route to local task queue
        result = lcs.longest_common_substr(task.string_a, task.string_b)
    task.lcs = result
    task.save()


@celery.shared_task
def do_local_lcs(str_a, str_b):
    pass


@celery.shared_task
def do_remote_lcs(str_a, str_b):
    pass


@celery.shared_task
def write_result(task_id, result):
    pass

