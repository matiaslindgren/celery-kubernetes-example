"""
Celery task wrapper for spotify2lyrics
"""
import spotify2genius
from celery import shared_task


# @shared_task
# def longest_common_substr(str_a, str_b):
#     return lcs.longest_common_substr(str_a, str_b)

@shared_task
def get_lyrics(user: str, playlist_id: str, project_name: str, debug: bool = False,
               num_threads: int = 4, threshold: int = 5):
    job = spotify2genius(user, playlist_id, project_name, debug, num_threads, threshold)
    job.big_function()
    return job.data
