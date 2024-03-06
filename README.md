# Aces Metrics Hanlder
Will operate in the EMDC level to extract metrics and efficiently organize them.
Licensed under MIT license

### Key Components
+ `Storage Components`: Object Storage (MinIO), Timeseries DB (TimescaleDB), Graph Store (Neo4j)
+ `Metrics Catalogue`: REST API that exposes stored information and data in all storages
+ `Pull-Push Metrics Pipelines`: Confluent Kafka, Prometheus, Metrics Scrapper
+ `Metrics Consumer`: Kafka Consumer which receives extracted metrics

### Installation Steps & Prerequisites

#### Storage Components
#### TimeScaleDB
1. `cd config/k8s/external/timescaledb`
2. `kubectl apply -f .`
3. `cd storage/timescaledb`
3. `python3 init_table.py`
#### Neo4j
4. `cd config/k8s/external/neo4j/standalone`
5. `bash setup.sh`
#### MinIO
6. `cd config/k8s/external/minio`
7. `kubectl apply -f pv.yaml`
8. `kustomize build infra | kubectl apply -f -`
9. `cd config/k8s/external/minio/mc`
10. `kubectl apply -f .`

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
