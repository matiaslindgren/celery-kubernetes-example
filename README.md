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

### Running locally

Please first install Minikube according to the installation instructions provided [here](https://github.com/kubernetes/minikube).
Minikube is a bit more challenging to get running than a simple Python package or systemd service, because Minikube will be running a VM.
The host system used in this example was an Ubuntu 16.04 with virtualization provided by KVM.

Start the Kubernetes cluster (replace the driver if not using KVM):
```
minikube start --vm-driver kvm2
```
Update the address of your RabbitMQ service in ``consumer/kube-deployment.yaml``.
If RabbitMQ is running locally, Minikube needs to access the host machine.
Minikube has created a virtual network and the host is (most likely) the first address, so the following address will probably work:
```
minikube ip | sed 's/[0-9]\+$/1/'
```
Now, build the Docker image for the consumer container.
First, set some environment variables for the current terminal instance to share the host Docker daemon with the Minikube VM:
```
eval (minikube docker-env)
```
Build the consumer container:
```
docker build --tag lcs:1 --file consumer/lcs.dockerfile .
```
Minikube should now be able to create containers from the ``lcs:1`` image.

Now, create a Deployment that deploys consumer containers into the local Kubernetes cluster:
```
kubectl create --filename consumer/kube-deployment.yaml
```

If Minikube cannot connect to its virtual network, check the state of the ``minikube-net`` network:
```
virsh net-list
```
If ``minikube-net`` is inactive:
```
virsh net-start minikube-net
```
Then start Minikube normally.
