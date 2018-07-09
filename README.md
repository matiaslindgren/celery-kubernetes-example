Toy example of a RESTful service computing long running tasks asynchronously in two different queues depending on input size.
Small input is routed to a local task consumer, while large input is routed to a remote Kubernetes cluster.

The service is represented by ``myproject`` and the long running tasks by the Python library ``lcs``, containing a poor implementation of a longest common substring algorithm.

### Sketch (autoscaling still WIP)

![architecture sketch](./celerykube.png)

### Requirements

* [Django](https://www.djangoproject.com)
* [Django REST framework](http://www.django-rest-framework.org)
* [Celery](http://www.celeryproject.org)
* [RabbitMQ](https://www.rabbitmq.com)
* [Minikube](https://github.com/kubernetes/minikube)
