from prefect import flow, get_run_logger, task
from prefect.variables import Variable
from base_etls import get_unique_pod_names, get_pod_metrics, parse_timeseries, \
    persist_to_minio, link_object_with_neo4j, delete_metrics_values


@task
def get_pods():
    pods = get_unique_pod_names()
    return pods


@task
def get_metrics(pod_name):
    pod_metrics = get_pod_metrics(pod_name)
    return pod_metrics


@task
def get_metric_df(metric_name, pod_name):
    df = parse_timeseries(
        metric=metric_name,
        pod=pod_name,
    )
    return df


@task
def move_to_minio(df, metric_name, pod_name):
    stored_df_obj = persist_to_minio(df, metric_name, pod_name)
    return stored_df_obj


@task
def assoc_obj_with_neo(obj, metric, pod):
    link_object_with_neo4j(obj, metric, pod)


@task
def delete_metrics(
        pod,
        metric,
        hours=1
):
    delete_metrics_values(pod, metric, hours)


@flow
def manage_metrics_flow():
    pods = get_pods()
    for pod in pods:
        this_pod_metrics = get_metrics(pod)
        for metric in this_pod_metrics:
            df = get_metric_df(metric, pod)
            stored_df_obj = move_to_minio(df, metric, pod)
            assoc_obj_with_neo(stored_df_obj, metric, pod)
            delete_metrics(pod, metric)
