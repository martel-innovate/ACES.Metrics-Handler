import datetime
import os

import pandas as pd

from object.client import MinioObject
from graph_base.base_client import GraphBase
from graph_base.api_client import ApiClient
from timescaledb.client import AcesMetrics

TSCALE_HOST = os.environ.get("TSCALE_HOST", "localhost")
TSCALE_USER = os.environ.get("TSCALE_NAME", "aces")
TSCALE_DB = os.environ.get("TSCALE_DB", "aces")
TSCALE_PASS = os.environ.get("TSCALE_PASS", "aces")

NEO4J_HOST = os.environ.get("NEO4J_HOST", "localhost")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASS", "neo4j290292")

MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'localhost')
MINIO_PORT = os.environ.get('MINIO_PORT', 9000)
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'admin')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'martel2024')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'emdc')

node = "node1"
# pod = "neo4j-0"
# metric = "container_blkio_device_usage_total"
aces_metrics = AcesMetrics(
    host=TSCALE_HOST,
    username=TSCALE_USER,
    database=TSCALE_DB,
    password=TSCALE_PASS
)

neo_client = GraphBase(
    neo4j_host=NEO4J_HOST,
    neo4j_user=NEO4J_USER,
    neo4j_pass=NEO4J_PASS
)
min_obj = MinioObject(
    endpoint=MINIO_ENDPOINT,
    port=MINIO_PORT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    bucket_name=BUCKET_NAME
)
api_client = ApiClient(
    neo4j_host=NEO4J_HOST,
    neo4j_user=NEO4J_USER,
    neo4j_pass=NEO4J_PASS
)


def parse_timeseries(
        metric,
        pod,
        node,
        aces_metrics_obj
):
    records = aces_metrics_obj.get_metric_tms(
        table_name="metrics_values",
        metric=metric,
        node=node,
        pod=pod,
    )
    df = pd.DataFrame(records)
    df.columns = ["timestamp", "value"]
    df['metric'] = metric
    return df


def persist_to_minio(
        df,
        minio_object,
        metric,
        pod,
        node
):
    extraction_date = str(datetime.datetime.now())
    obj = minio_object.put_csv(
        df,
        f"{node}/{pod}/{metric}/{extraction_date}.csv"
    )
    return obj


pods = aces_metrics.fetch_unique_pods(table_name="metrics_values", node="node1")
for pod in pods:
    pod_metrics = aces_metrics.fetch_pod_metrics(table_name="metrics_values", node="node1", pod=pod)

    for metric in pod_metrics:
        df = parse_timeseries(
            metric=metric,
            node=node,
            pod=pod,
            aces_metrics_obj=aces_metrics
        )
        obj = persist_to_minio(
            df=df,
            minio_object=min_obj,
            metric=metric,
            pod=pod,
            node=node
        )
        object_name = obj._object_name
        object_root_folder = "/".join(
            object_name.split("/")[:-1]
        )
        api_client.link_object_with_pod(
            object_name=object_root_folder,
            pod=pod,
            node=node,
            metric=metric
        )
        aces_metrics.delete_metrics_in_range(
            table_name='metrics_values',
            node="node1",
            pod=pod,
            metric=metric,
            hours=3
        )
