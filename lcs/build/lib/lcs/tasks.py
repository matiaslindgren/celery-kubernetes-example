"""
Celery task wrapper for longest_common_substr.
"""
import lcs
from celery import shared_task

@shared_task
def longest_common_substr(str_a, str_b):
    return lcs.longest_common_substr(str_a, str_b)
