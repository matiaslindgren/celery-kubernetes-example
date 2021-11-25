"""
Interface for launching asynchronous Celery tasks.
"""
import celery
import lcs.tasks
import spotify2genius.tasks

import database
import settings


def make_celery(app):
    # https://flask.palletsprojects.com/en/1.1.x/patterns/celery/
    c = celery.Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    c.conf.update(app.config)
    class ContextTask(c.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    c.Task = ContextTask
    return c

def create_s2p_task(user: str, playlist_id: str, project_name: str, debug: bool = False,
               num_threads: int = 4, threshold: int = 5):
    """
    Create new async task to compute lcs on str_a and str_b.
    """

    task_id = database.create_task()

    # Choose queue depending on input size
    # if max(len(str_a), len(str_b)) > settings.large_tasks_size_threshold:
    #     queue_options = {"queue": "large_tasks"}
    # else:
    queue_options = {"queue": "small_tasks"}


    # Create async tasks for Celery
    compute_s2p_task = spotify2genius.tasks.get_lyrics.signature(
        (user, playlist_id, project_name, debug,
        num_threads, threshold),
        immutable=True, options=queue_options)

    write_result_task = write_result.signature(
        (task_id,),
        options={"queue": "small_tasks"})
    # Chain both tasks and put them on the queues
    (compute_s2p_task | write_result_task).apply_async()
    return task_id


def create_lcs_task(str_a, str_b):
    """
    Create new async task to compute lcs on str_a and str_b.
    """
    task_id = database.create_task()
    # Choose queue depending on input size
    if max(len(str_a), len(str_b)) > settings.large_tasks_size_threshold:
        queue_options = {"queue": "large_tasks"}
    else:
        queue_options = {"queue": "small_tasks"}
    # Create async tasks for Celery
    compute_lcs_task = lcs.tasks.longest_common_substr.signature(
        (str_a, str_b),
        immutable=True,
        options=queue_options)
    write_result_task = write_result.signature(
        (task_id,),
        options={"queue": "small_tasks"})
    # Chain both tasks and put them on the queues
    (compute_lcs_task | write_result_task).apply_async()
    return task_id

@celery.shared_task(name="myproject.tasks.write_result", ignore_result=True)
def write_result(result, task_id):
    database.finish_task(task_id, result)
