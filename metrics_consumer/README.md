# METRICS CONSUMER Installation guides

1. `build the Dockerfile`

```shell
docker build -f metrics_consumer/Dockerfile -t pkapsalismartel/metrics_consumer .
docker tag pkapsalismartel/metrics_consumer:latest pkapsalismartel/metrics_consumer:v0.3
docker push pkapsalismartel/metrics_consumer:v0.3
```