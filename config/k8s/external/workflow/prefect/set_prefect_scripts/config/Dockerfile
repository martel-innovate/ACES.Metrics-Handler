FROM python:3.9-slim

WORKDIR /opt/setup

RUN pip install s3fs
RUN pip install minio
RUN pip install boto3
RUN pip install prefect
RUN pip install neo4j
RUN pip install psycopg2-binary

COPY config/scripts .
CMD bash run.sh