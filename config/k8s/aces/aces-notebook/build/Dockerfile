FROM jupyter/scipy-notebook

WORKDIR /opt/aces

COPY config/k8s/aces/aces-notebook/build/requirements.txt .
COPY  config/k8s/aces/aces-notebook/build/run.sh .

RUN pip install -r requirements.txt
RUN bash run.sh