FROM python:3.9

RUN apt-get update \
 && apt-get install --assume-yes --no-install-recommends --quiet \
    ca-certificates \
    cmake \
    git \
    g++ \
    make \
    libzip-dev \
 && apt-get clean all

RUN pip install jupyter

EXPOSE 8888
ENTRYPOINT ["jupyter", "notebook","--allow-root","--ip=0.0.0.0","--port=8888"]