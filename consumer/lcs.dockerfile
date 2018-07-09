FROM alpine:3.7
COPY lcs /usr/share/lcs
COPY consumer/lcs_celery.py /usr/share/lcs_celery.py
RUN apk add --no-cache python3 \
    && python3 -m pip install celery -e /usr/share/lcs
ENTRYPOINT python3 /usr/share/lcs_celery.py --app lcs_celery --concurrency 1 --queue large_tasks --loglevel=INFO
