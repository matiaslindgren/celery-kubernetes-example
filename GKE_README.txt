make sure gcloud sdk is installed and pathed correctly

gcloud auth login
gcloud projects list
gcloud config set project MY_PROJECT_NAME


# push the images to google contianer registry
gcloud auth configure-docker

docker build --tag myproject:1 --file myproject/Dockerfile .
docker tag myproject:1 gcr.io/first-304221/myproject:1
docker push gcr.io/first-304221/myproject:1

docker build --tag consumer-small:1 --file consumer-small/Dockerfile .
docker tag consumer-small:1 gcr.io/first-304221/consumer-small:1
docker push gcr.io/first-304221/consumer-small:1

docker build --tag consumer-large:1 --file consumer-large/Dockerfile .
docker tag consumer-large:1 gcr.io/first-304221/consumer-large:1
docker push gcr.io/first-304221/consumer-large:1


# GKE
gcloud components install kubectl

gcloud config set project MY_PROJECT_NAME
gcloud config set compute/zone ZONE_NAME


# -------- my-celery-cluster -------------
gcloud container clusters create my-celery-cluster --num-nodes=1 \
--preemptible \
--enable-autoscaling --max-nodes=5 --min-nodes=1

gcloud container clusters get-credentials my-celery-cluster


kubectl create -f message_queue/rabbitmq-deployment.yaml
kubectl create -f message_queue/rabbitmq-service.yaml


# I changed the yml to point to the image in gcr
kubectl create -f myproject/deployment.yaml
kubectl create -f consumer-large/deployment.yaml

kubectl get pods


# to find external ip
kubectl get service myproject-svc


# DELETE CLUSTER to avoid addtional charges
gcloud container clusters delete my-celery-cluster








