# METRICS CONSUMER Installation guides

1. `build the Dockerfile`

```shell
docker build -f metrics_consumer/Dockerfile -t pkapsalismartel/metrics_consumer .
docker tag pkapsalismartel/metrics_consumer:latest pkapsalismartel/metrics_consumer:v0.11
docker push pkapsalismartel/metrics_consumer:v0.11
```

2. `Commands to execute for the Kafka Broker`
Firstly you need to connect to Kafka Broker pod for instance:
```shell
kubectl exec -it ${kafka_broker_pod_id} bash
```

Describe a consumer group
```shell
kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group aces_metrics_consumer
```
Describe a topic
```shell
kafka-topics --bootstrap-server localhost:9092 --describe --topic metrics
```

Alter a topic (change partitions)
```shell
kafka-topics --bootstrap-server localhost:9092 --alter --topic metrics --partitions 2
```

List all topics
```shell
 kafka-topics --list --bootstrap-server localhost:9092
```