import datetime
import os

import pandas as pd

from storage.object.client import MinioObject
from storage.graph_base.base_client import GraphBase
from storage.graph_base.api_client import ApiClient
from storage.timescaledb.client import AcesMetrics

from settings import TSCALE_HOST, TSCALE_USER, TSCALE_DB, TSCALE_PASS, \
    NEO4J_HOST, NEO4J_USER, NEO4J_PASS, MINIO_ENDPOINT, MINIO_PORT, MINIO_ACCESS_KEY, \
    MINIO_SECRET_KEY, BUCKET_NAME, TSCALE_TABLE, node

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


def get_unique_pod_names():
    pods = aces_metrics.fetch_unique_pods(table_name=TSCALE_TABLE, node=node)
    return pods


def get_pod_metrics(pod_name):
    pod_metrics = aces_metrics.fetch_pod_metrics(
        table_name=TSCALE_TABLE,
        node=node,
        pod=pod_name
    )
    return pod_metrics


def parse_timeseries(
        metric,
        pod,
        node=node
):
    records = aces_metrics.get_metric_tms(
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
        metric,
        pod,
        node=node
):
    extraction_date = str(datetime.datetime.now())
    obj = min_obj.put_csv(
        df,
        f"{node}/{pod}/{metric}/{extraction_date}.csv"
    )
    return obj


def link_object_with_neo4j(stored_obj, metric, pod, node=node):
    api_client = ApiClient(
        neo4j_host=NEO4J_HOST,
        neo4j_user=NEO4J_USER,
        neo4j_pass=NEO4J_PASS
    )
    object_name = stored_obj._object_name
    object_root_folder = "/".join(
        object_name.split("/")[:-1]
    )
    api_client.link_object_with_pod(
        object_name=object_root_folder,
        pod=pod,
        node=node,
        metric=metric
    )
    api_client.session.close()


def delete_metrics_values(
        pod, metric,
        hours, table_name=TSCALE_TABLE,
        node=node
):
    aces_metrics.delete_metrics_in_range(
        table_name=table_name,
        node=node,
        pod=pod,
        metric=metric,
        hours=hours
    )
