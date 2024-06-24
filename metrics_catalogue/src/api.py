import logging
import sys
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from graph_base.demand import DemandGraph
from graph_base.supply import SupplyGraph
from graph_base.api_client import ApiClient
from timescaledb.client import AcesMetrics
from object.client import MinioObject

from settings import NEO4J_HOST, NEO4J_USER, NEO4J_PASS, TSCALE_HOST, TSCALE_USER, TSCALE_DB, TSCALE_PASS, \
    MINIO_ENDPOINT, MINIO_PORT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, BUCKET_NAME

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

tags_metadata = [
    {"name": "Init Phase", "description": "Initialize Metrics Management"},
    {"name": "Pod Metrics APIs", "description": "APIs to manage Pod Metrics"},
    {"name": "Pod Status APIs", "description": "APIs to manage Pod Status"},
    {"name": "Container Metrics APIs", "description": "APIs to manage Container Metrics"},
    {"name": "Historical", "description": "APIs to manage historic information"},
    {"name": "Node Metrics APIs", "description": "APIs to manage Node Metrics"},
]

app = FastAPI(openapi_tags=tags_metadata)

aces_metrics = AcesMetrics(
    host=TSCALE_HOST,
    username=TSCALE_USER,
    database=TSCALE_DB,
    password=TSCALE_PASS
)

minio_object = MinioObject(
    endpoint=MINIO_ENDPOINT,
    port=MINIO_PORT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    bucket_name=BUCKET_NAME
)


def init_graph_base():
    supply_agent = SupplyGraph(
        neo4j_host=NEO4J_HOST,
        neo4j_user=NEO4J_USER,
        neo4j_pass=NEO4J_PASS
    )
    demand_agent = DemandGraph(
        neo4j_host=NEO4J_HOST,
        neo4j_user=NEO4J_USER,
        neo4j_pass=NEO4J_PASS
    )
    return supply_agent, demand_agent


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class NodeStatus(Enum):
    Active = 'Active'
    Inactive = 'Inactive'


class CPUBody(BaseModel):
    cpu_id: Optional[str] = Field(default="undefined_cpu", description="CPU Id")
    model: Optional[str] = Field(default="undefined", description="CPU model")
    cores: Optional[int] = Field(default=0, description="CPU Cores")


class GPUBody(BaseModel):
    gpu_id: Optional[str] = Field(default="undefined_gpu", description="GPU Id")
    model: Optional[str] = Field(default="undefined", description="GPU model")


class NodeBody(BaseModel):
    node_id: str = Field(..., description="Node Id")
    status: NodeStatus
    cpu: Optional[CPUBody] = None
    gpu: Optional[GPUBody] = None


@app.get('/nodes/pods', tags=["Pod Metrics APIs"])
async def get_node_pods():
    supply_agent, demand_agent = init_graph_base()
    query = demand_agent.get_node_pods(node_id='node1')
    results = demand_agent.emit_transaction(query)
    list_of_pods = results[0]["list_of_pods"]
    list_of_res = list(map(
        lambda d: d['pod_id'],
        [pod._properties for pod in list_of_pods]
    ))
    demand_agent.session.close()
    return list_of_res


@app.get('/container/metrics', tags=["Container Metrics APIs"])
async def get_metrics():
    supply_agent, demand_agent = init_graph_base()
    query = demand_agent.get_list_of_metrics()
    results = demand_agent.emit_transaction(query)
    list_of_metrics = [
        metric["m"]._properties["name"]
        for metric in results if metric["m"]._properties["name"].startswith("container_")
    ]
    demand_agent.session.close()
    return list_of_metrics


@app.get('/pod/{pod_id}/phase', tags=["Pod Status APIs"])
async def get_pod_phase(pod_id: str):
    results = aces_metrics.get_pod_status(pod_id)
    return results


@app.get('/pod/{pod_id}/phase/history', tags=["Pod Status APIs"])
async def get_pod_phase_hist(pod_id: str):
    list_of_res = aces_metrics.pod_status_hist(pod_id)
    return list_of_res


@app.get('/nodes/pod/{pod_id}/container/metrics/{metric_id}', tags=["Container Metrics APIs"])
async def get_spec_metrics(
        pod_id: str,
        metric_id: str
):
    node_id = 'node1'
    supply_agent, demand_agent = init_graph_base()
    query = demand_agent.specific_pod_metric(
        node_id,
        pod_id,
        metric_id
    )
    tms_table = demand_agent.emit_transaction(query)[0]['origin']
    records = aces_metrics.get_metric_tms(
        table_name=tms_table,
        metric=metric_id,
        node=node_id,
        pod=pod_id
    )
    tms = [
        {
            "time": record[0],
            "value": record[1]
        } for record in records]
    demand_agent.session.close()
    return tms


@app.get('/pod/{pod_id}/restarts', tags=["Pod Status APIs"])
def get_pod_restarts(pod_id: str):
    results = aces_metrics.get_pod_restarts(pod_id)
    return results


@app.get('/init', tags=["Init Phase"])
async def init_catalogue():
    supply_agent, demand_agent = init_graph_base()
    query_emdc = supply_agent.insert_emdc(
        emdc_id="this_emdc",
        location="localhost"
    )
    supply_agent.exec(query_emdc)
    query_cluster = supply_agent.insert_cluster(
        emdc_id="this_emdc",
        cluster_id="this_cluster",
        node_count=1
    )
    supply_agent.exec(query_cluster)
    query_node = supply_agent.insert_node(
        cluster_id="this_cluster",
        node_id="node1",
        node_status="ACTIVE",
        cpu_id="node1_cpu",
        gpu_id="node1_gpu",
        cores=4
    )
    supply_agent.exec(query_node)
    supply_agent.session.close()
    aces_metrics.init_aces_hyper_table("metrics_values")
    aces_metrics.init_aces_node_hyper_table("node_metrics")
    aces_metrics.init_aces_pod_phase("pod_phase")
    aces_metrics.init_container_resource_limits()
    aces_metrics.init_container_resource_requests()
    aces_metrics.init_pod_utilization()
    aces_metrics.init_kubelet_metrics_table()
    return {"msg": "Initialization completed"}


@app.get('/nodes/pods/{pod_id}/history/', tags=["Historical"])
async def get_node_hist(node_id: str, pod_id: str):
    node_id = 'node1'
    results = minio_object.list_objects_(
        bucket_name=BUCKET_NAME,
        prefix=f"{node_id}/{pod_id}/"
    )
    return results


@app.get('/nodes/pods/{pod_id}/metric/{metric_id}/history/', tags=["Historical"])
async def get_node_metric_hist(node_id: str, pod_id: str, metric_id: str):
    node_id = 'node1'
    results = minio_object.list_objects_(
        bucket_name=BUCKET_NAME,
        prefix=f"{node_id}/{pod_id}/{metric_id}",
        recursive=True
    )
    return results


@app.get('/historical/storage/pods', tags=["Historical"])
async def get_historical_data_links():
    api_client = ApiClient(
        neo4j_host=NEO4J_HOST,
        neo4j_user=NEO4J_USER,
        neo4j_pass=NEO4J_PASS
    )
    results = api_client.get_pods_in_history()
    api_client.session.close()
    return results


@app.get('/nodeInfo', tags=["Node Metrics APIs"])
async def get_node_info():
    supply_agent, demand_agent = init_graph_base()
    query = demand_agent.get_node_info()
    results = demand_agent.emit_transaction(query)
    demand_agent.session.close()
    return results


@app.get('/nodeRole', tags=["Node Metrics APIs"])
async def get_node_role():
    supply_agent, demand_agent = init_graph_base()
    query = demand_agent.get_node_role()
    results = demand_agent.emit_transaction(query)
    demand_agent.session.close()
    return results


@app.get('/nodeCapacity/topology', tags=["Node Metrics APIs"])
async def get_node_capacity():
    supply_agent, demand_agent = init_graph_base()
    query = demand_agent.get_node_capacity_topology()
    results = demand_agent.emit_transaction(query)
    demand_agent.session.close()
    return results


@app.get('/nodeCapacity/resource/{resource_name}', tags=["Node Metrics APIs"])
async def node_resources(resource_name: str):
    supply_agent, demand_agent = init_graph_base()
    query = demand_agent.get_resource_details(resource_name)
    results = demand_agent.emit_transaction(query)[0]
    if results:
        metric_name = results["metric_name"]
        demand_agent.session.close()
        resource_tms = aces_metrics.fetch_node_metrics(
            table_name="node_metrics",
            metric=metric_name
        )
        results["tms"] = resource_tms
    return results


@app.get('/kubelet/metrics', tags=["Node Metrics APIs"])
def get_kubelet_metrics():
    supply_agent, demand_agent = init_graph_base()
    query = demand_agent.fetch_kubelet_metrics()
    results = demand_agent.emit_transaction(query)
    demand_agent.session.close()
    kubelet_metrics = [record['metric'] for record in results]
    return kubelet_metrics


@app.get('/kubelet/metrics/{metric}/tms', tags=["Node Metrics APIs"])
def get_kubelet_metric_tms(metric: str):
    tms_records = aces_metrics.get_kubelet_metric_tms(metric)
    return tms_records


@app.get('/pod/{pod_id}/resource/requests', tags=["Pod Metrics APIs"])
async def pod_resource_requests(pod_id: str):
    result_tuples = aces_metrics.get_pod_resource_reqs(pod_id)
    return result_tuples


@app.get('/pod/{pod_id}/utilization', tags=["Pod Metrics APIs"])
async def pod_util(pod_id: str):
    results = aces_metrics.get_pod_utilization_details(pod_id)
    return results


@app.get('/pod/{pod_id}/resource/limits', tags=["Pod Metrics APIs"])
async def pod_resource_limits(pod_id: str):
    result_tuples = aces_metrics.get_pod_resource_limits(pod_id)
    return result_tuples

# uvicorn api:app --reload --host 0.0.0.0
