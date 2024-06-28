# METRICS Catalogue Installation guides

```shell
docker build -f metrics_catalogue/Dockerfile -t pkapsalismartel/metrics_catalogue .
docker tag pkapsalismartel/metrics_catalogue:latest pkapsalismartel/metrics_catalogue:v0.26
docker push pkapsalismartel/metrics_catalogue:v0.26
```