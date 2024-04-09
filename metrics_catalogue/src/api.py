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
    {"name": "EMDC APIs", "description": "APIs to manage EMDC Info"},
    {"name": "Cluster APIs", "description": "APIs to manage Clusters"},
    {"name": "Node APIs", "description": "APIs to manage Nodes"},
    {"name": "Pod APIs", "description": "APIs to manage Pods"},
    {"name": "Metric APIs", "description": "APIs to manage Metrics"},
    {"name": "Metrics in Pods APIs", "description": "APIs to manage Metrics related to Pods"},
    {"name": "Historical", "description": "APIs to manage historic information"},

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


class EMDCBody(BaseModel):
    emdc_id: str = Field(..., description="EMDC ID")
    location: str = Field(..., description="EMDC Location")


class ClusterBody(BaseModel):
    cluster_id: str = Field(..., description="EMDC cluster ID")
    node_count: int = Field(..., description="Number of Cluster Nodes")


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


@app.post('/set/emdcs', tags=["EMDC APIs"])
async def insert_emdc(item_body: EMDCBody):
    supply_agent, demand_agent = init_graph_base()
    this_body = item_body.__dict__
    log.info(f"insert EMDC with ID: {this_body['emdc_id']} and Location: {this_body['location']}")
    query = supply_agent.insert_emdc(
        emdc_id=this_body["emdc_id"],
        location=this_body["location"]
    )
    supply_agent.exec(query)
    supply_agent.session.close()
    return {"msg": "EMDC inserted"}, 201


@app.post('/set/emdcs/{emdc_id}/clusters', tags=["EMDC APIs"])
async def insert_cluster(cluster_body: ClusterBody, emdc_id: str):
    this_cluster_body = cluster_body.__dict__
    supply_agent, demand_agent = init_graph_base()
    log.info(
        f"insert Cluster with ID: {this_cluster_body['cluster_id']} and"
        f" Location: {this_cluster_body['node_count']} to EMDC {emdc_id}"
    )
    query = supply_agent.insert_cluster(
        emdc_id=emdc_id,
        cluster_id=this_cluster_body["cluster_id"],
        node_count=this_cluster_body["node_count"]
    )
    supply_agent.bolt_transaction(query)
    supply_agent.session.close()
    return {"msg": "Cluster inserted"}, 201


@app.post('/set/cluster/{cluster_id}/nodes', tags=["Cluster APIs"])
async def insert_node(node_body: NodeBody, cluster_id: str):
    node_input = node_body
    supply_agent, demand_agent = init_graph_base()
    log.info(f"Insert Node with ID: {node_input.node_id} to cluster with ID: {cluster_id}")
    query = supply_agent.insert_node(
        cluster_id=cluster_id,
        node_id=node_input.node_id,
        node_status=node_input.status.value,
        cpu_id=node_input.cpu.cpu_id,
        gpu_id=node_input.gpu.gpu_id,
        cores=node_input.cpu.cores
    )
    supply_agent.exec(query)
    supply_agent.session.close()
    return {"msg": "Node inserted"}, 201


@app.get('/cluster/{cluster_id}', tags=["Cluster APIs"])
async def get_cluster(cluster_id: str):
    supply_agent, demand_agent = init_graph_base()
    query = supply_agent.get_cluster_info(cluster_id=cluster_id)
    results = supply_agent.emit_transaction(query)
    this_result = results[0]
    cluster_info = this_result['cl']._properties
    nodes = [n._properties for n in this_result['nodes']]
    cluster_info['nodes'] = nodes
    supply_agent.session.close()
    return cluster_info, 200


@app.get('/nodes/{node_id}', tags=["Node APIs"])
async def get_node(node_id: str):
    supply_agent, demand_agent = init_graph_base()
    query = supply_agent.get_node_info(node_id)
    results = supply_agent.emit_transaction(query)
    this_result = results[0]
    node_info = this_result['n']._properties
    node_info['objs'] = [
        {
            'type': list(obj._labels)[0],
            'values': obj._properties
        } for obj in this_result['objs']
    ]
    supply_agent.session.close()
    return node_info


@app.get('/nodes/{node_id}/pods', tags=["Pod APIs"])
async def get_node_pods(node_id: str):
    supply_agent, demand_agent = init_graph_base()
    query = demand_agent.get_node_pods(node_id)
    results = demand_agent.emit_transaction(query)
    list_of_pods = results[0]["list_of_pods"]
    list_of_res = list(map(
        lambda d: d['pod_id'],
        [pod._properties for pod in list_of_pods]
    ))
    demand_agent.session.close()
    return list_of_res


@app.get('/metrics', tags=["Metric APIs"])
async def get_metrics():
    supply_agent, demand_agent = init_graph_base()
    query = demand_agent.get_list_of_metrics()
    results = demand_agent.emit_transaction(query)
    list_of_metrics = [metric["m"]._properties["name"] for metric in results]
    demand_agent.session.close()
    return list_of_metrics


@app.get('/nodes/{node_id}/pod/{pod_id}/metrics', tags=["Metrics in Pods APIs"])
async def get_pod_metrics(node_id: str, pod_id: str):
    supply_agent, demand_agent = init_graph_base()
    query = demand_agent.get_pod_metrics(node_id, pod_id)
    results = demand_agent.emit_transaction(query)[0]['pod_metrics']
    pod_metrics = [metric._properties["name"] for metric in results]
    demand_agent.session.close()
    return pod_metrics


@app.get('/nodes/{node_id}/pod/{pod_id}/metrics/{metric_id}', tags=["Metrics in Pods APIs"])
async def get_spec_metrics(
        node_id: str,
        pod_id: str,
        metric_id: str
):
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
    return {"msg": "Init was finalized"}


@app.get('/nodes/{node_id}/pods/{pod_id}/history/', tags=["Historical"])
async def get_node_hist(node_id: str, pod_id: str):
    results = minio_object.list_objects_(
        bucket_name=BUCKET_NAME,
        prefix=f"{node_id}/{pod_id}/"
    )
    return results


@app.get('/nodes/{node_id}/pods/{pod_id}/metric/{metric_id}/history/', tags=["Historical"])
async def get_node_metric_hist(node_id: str, pod_id: str, metric_id: str):
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
# uvicorn api:app --reload --host 0.0.0.0
