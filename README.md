# Aces Metrics Hanlder
Will operate in the EMDC level to extract metrics and efficiently organize them.
Licensed under MIT license

### Key Components
+ `Storage Components`: Object Storage (MinIO), Timeseries DB (TimescaleDB), Graph Store (Neo4j)
+ `Metrics Catalogue`: REST API that exposes stored information and data in all storages
+ `Pull-Push Metrics Pipelines`: Confluent Kafka, Prometheus, Metrics Scrapper
+ `Metrics Consumer`: Kafka Consumer which receives extracted metrics

### Installation Steps & Prerequisites
#### Install Workflow Components
```shell
cd config/external/k8s/workflow
```
##### Install Minio
```shell
cd minio/
kubectl apply -f pv.yaml
kustomize build infra | kubectl apply -f -
cd mc/
kubectl apply -f .
```
##### Install & Configure Prefect Server
```shell
cd prefect/
bash make_server.sh
cd set_prefect_scripts/
kubectl apply -f deployment.yaml
cd ../
bash make_agent.sh
kubectl port-forward svc/prefect-server 4200:4200
```
##### Install Jupyter Notebook
```shell
cd jupyter/
kubectl apply -f .
kubectl port-forward svc/notebook 8888:8888
```
##### Deploy ETLs to Prefect Workflow Orchestrator
```shell
prefect deployment build flows/manage_metrics_flow.py:manage_metrics_flow -n 'manage_metrics_flow' -ib kubernetes-job/prod -sb 'remote-file-system/minio' --pool aces
prefect deployment apply manage_metrics_flow-deployment.yaml 
```



#### Metrics Catalogue
0. `How to build Metrics catalogue dockerfile` see documentation [here](metrics_catalogue/README.md)
1. `cd /config/k8s/aces/metrics_catalogue`
2. `kubectl apply -f .`

#### Pull-push Metrics Pipeline
##### Deploy Confluent Kafka
1. `cd config/k8s/external/kafka`
2. `kubectl apply -f .`
##### Deploy Prometheus
1. `cd config/k8s/external/prometheus`
2. `bash setup.sh`
##### Deploy Metrics Scraper
1. `cd config/k8s/external/prom-adapter`
2. `kubectl apply -f .`

#### Metrics Consumer
0. `How to build Metrics consumer dockerfile` see documentation [here](metrics_consumer/README.md)
1. `cd /config/k8s/aces/metrics_consumer`
2. `kubectl apply -f .`