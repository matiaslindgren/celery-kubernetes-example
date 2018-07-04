import os
import celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = celery.Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
