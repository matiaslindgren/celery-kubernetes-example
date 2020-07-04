FROM alpine:3.12
COPY lcs /usr/src/lcs
COPY consumer-large/celery_app.py /usr/bin/celery_app.py
RUN apk add --no-cache python3 py3-pip bash \
    && pip install 'celery~=4.4.0' /usr/src/lcs
ENTRYPOINT python3 /usr/bin/celery_app.py \
    --concurrency 2 \
    --queues large_tasks \
    --loglevel INFO
