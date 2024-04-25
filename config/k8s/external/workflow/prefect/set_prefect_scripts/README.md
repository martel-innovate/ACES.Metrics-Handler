```shell
docker build -f config/Dockerfile -t pkapsalismartel/aces_emdc_prefect .
docker tag pkapsalismartel/aces_emdc_prefect:latest pkapsalismartel/aces_emdc_prefect:v0.1
docker push pkapsalismartel/aces_emdc_prefect:v0.1
```