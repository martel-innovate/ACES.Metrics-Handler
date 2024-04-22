```shell
 docker build -f config/k8s/aces/aces-notebook/build/Dockerfile -t pkapsalismartel/aces-notebook .
 docker tag pkapsalismartel/aces-notebook:latest pkapsalismartel/aces-notebook:v0.3
 docker push pkapsalismartel/aces-notebook:v0.3
```