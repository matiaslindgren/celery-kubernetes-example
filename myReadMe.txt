make sure gcloud sdk is installed and pathed wasnt getting path to work so I just run the installer.sh

gcloud auth login
gcloud projects list
gcloud config set project first-304221

# building images 
docker build --tag myproject:1 --file myproject/Dockerfile .
docker build --tag consumer-small:1 --file consumer-small/Dockerfile .
docker build --tag consumer-large:1 --file consumer-large/Dockerfile .
docekr images

# push the images to google contianer registry
gcloud auth configure-docker

# docker build -t pythonrestapi .
# docker tag [SOURCE_IMAGE] [HOSTNAME]/[PROJECT-ID]/[IMAGE]:[TAG]
# // run this command
# docker tag pythonrestapi gcr.io/staticweb-test/restapi:v1
# docker push gcr.io/staticweb-test/restapi:v1

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

gcloud config set project first-304221
gcloud config set compute/zone us-east1-d

gcloud container clusters create my-celery-cluster --num-nodes=1 \
--preemptible \
--enable-autoscaling --max-nodes=5 --min-nodes=1

gcloud container clusters get-credentials my-celery-cluster


kubectl create --filename message_queue/rabbitmq-deployment.yaml
kubectl create --filename message_queue/rabbitmq-service.yaml


# I changed the yml to point to the image in gcr (had to repush images?)
kubectl create --filename myproject/deployment.yaml

kubectl create --filename consumer-large/deployment.yaml

kubectl get pods

kubectl port-forward deployment/myproject 5000:5000

kubectl get service myproject --output yaml

kubectl port-forward service/myproject 5000

gcloud container clusters delete my-celery-cluster






