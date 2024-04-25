import os
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
pod = "neo4j-0"
metric = "container_blkio_device_usage_total"
aces_metrics = AcesMetrics(
    host=TSCALE_HOST,
    username=TSCALE_USER,
    database=TSCALE_DB,
    password=TSCALE_PASS
)
results = aces_metrics.metrics_value_range(
    table_name="metrics_values",
    node="node1",
    pod='neo4j-0',
    metric="container_spec_cpu_shares",
    hours=3
)
print(results)

# from graph_base.api_client import ApiClient
# api_client = ApiClient(
#     neo4j_host=NEO4J_HOST,
#     neo4j_user=NEO4J_USER,
#     neo4j_pass=NEO4J_PASS
# )
# results = api_client.get_pods_in_history()
# print(results)