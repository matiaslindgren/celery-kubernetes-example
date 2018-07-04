Simple Django app with Celery workers that need to handle asynchronously lightweight and cpu-heavy tasks.
Lightweight tasks are processed in a local queue, while the cpu-heavy tasks are routed to a Kubernetes node that scales automatically.

Everything runs locally in this example, but in a production environment, it would make more sense to have the Kubernetes node in the cloud.

### Requirements

* Django
* Celery
* Jinja2
* RabbitMQ
