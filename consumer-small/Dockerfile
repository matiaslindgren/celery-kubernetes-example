FROM myproject:1
WORKDIR /usr/src/myproject
ENTRYPOINT celery worker \
    --app main.celery_app \
    --queues small_tasks \
    --concurrency 1 \
    --loglevel INFO
