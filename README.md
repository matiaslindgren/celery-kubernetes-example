Simple Django app with Celery workers computing longest common substring tasks asynchronously in separate processes.
Lightweight tasks, i.e. small input, are processed in a local queue, while larger input is routed to a Kubernetes node, which in turn can be located in the cloud and could be configured to scale automatically.

### Requirements

* [Django](https://www.djangoproject.com)
* [Django REST framework](http://www.django-rest-framework.org)
* [Celery](http://www.celeryproject.org)
* [RabbitMQ](https://www.rabbitmq.com)
* [minikube](https://github.com/kubernetes/minikube)
