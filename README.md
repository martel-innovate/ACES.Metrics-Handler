# Aces Metrics Hanlder
Will operate in the EMDC level to extract metrics and efficiently organize them.
Licensed under MIT license

### Key Components
+ `Storage Components`: Object Storage (MinIO), Timeseries DB (TimescaleDB), Graph Store (Neo4j)
+ `Metrics Catalogue`: REST API that exposes stored information and data in all storages
+ `Pull-Push Metrics Pipelines`: Confluent Kafka, Prometheus, Metrics Scrapper
+ `Metrics Consumer`: Kafka Consumer which receives extracted metrics

### Installation Steps & Prerequisites
#### 1. Install Workflow Components
```shell
cd config/external/k8s/workflow
```
##### 1.1 Install Minio
```shell
cd minio/
kubectl apply -f pv.yaml
kustomize build infra | kubectl apply -f -
cd mc/
kubectl apply -f .
```
##### 1.2 Install & Configure Prefect Server
```shell
cd prefect/
bash make_server.sh
cd set_prefect_scripts/
kubectl apply -f deployment.yaml
cd ../
bash make_agent.sh
```
##### 1.3 Install Jupyter Notebook
```shell
cd jupyter/
kubectl apply -f .
```

##### 1.4 Port forward Workflow Services
###### 1.4.1 MinIO Console
```shell
 kubectl port-forward svc/console 9090:9090 -n minio-operator
 kubectl describe secrets/console-sa-secret -n minio-operator
```
###### 1.4.2 Prefect Server UI
```shell
kubectl port-forward svc/prefect-server 4200:4200
```
###### 1.4.3 Jupyter Notebook
```shell
kubectl port-forward svc/notebook 8888:8888
```

##### Deploy ETLs to Prefect Workflow Orchestrator
```shell
prefect deployment build flows/manage_metrics_flow.py:manage_metrics_flow -n 'manage_metrics_flow' -ib kubernetes-job/prod -sb 'remote-file-system/minio' --pool aces
prefect deployment apply manage_metrics_flow-deployment.yaml 
```

#### 2. Storage Components
```shell
cd config/k8s/external/storage-components
```
##### 2.1 Install Neo4j
```shell
cd neo4j/standalone
bash setup.sh
```
##### 2.2 Install TimescaleDB
```shell
cd timescaledb
kubectl apply -f .
```
##### 2.3 Port Forward Storage Components
###### 2.3.1 Neo4j
```shell
kubectl port-forward svc/neo4j 7474:7474
```
###### 2.3.2 Timescaledb
```shell
kubectl port-forward svc/timescaledb 5432:5432
cd storage/timescaledb
python init_table.py
```
#### 3. Metrics Catalogue
0. `How to build Metrics catalogue dockerfile` see documentation [here](metrics_catalogue/README.md)
2. `cd config/k8s/aces/metrics_catalogue`
3. `kubectl apply -f .`
4. `kubectl port-forward svc/metrics-catalogue 8000:8000`
5. Init the Metrics Management System using the following CURL API
```shell
curl -X 'GET' \
  'http://localhost:8000/init' \
  -H 'accept: application/json'
```

#### 4. Pull-push Metrics Pipeline
`cd config/k8s/external/pull-push-pipeline`
##### 4.1 Deploy Confluent Kafka
1. `cd kafka`
2. `kubectl apply -f .`
##### 4.2 Deploy Prometheus
1. `cd prometheus`
2. `bash setup.sh`
##### 4.3 Deploy Metrics Scraper
1. `cd prom-adapter`
2. `kubectl apply -f .`

##### 4.4 Port Forward Control Center
```shell
kubectl port-forward svc/control-center 9021:9021
```
#### 5. Metrics Consumer
0. `How to build Metrics consumer dockerfile` see documentation [here](metrics_consumer/README.md)
1. `cd config/k8s/aces/metrics_consumer`
2. `kubectl apply -f .`