import os

node = 'node1'
# timescaledb settings
TSCALE_HOST = os.environ.get("TSCALE_HOST", "timescaledb")
TSCALE_USER = os.environ.get("TSCALE_NAME", "aces")
TSCALE_DB = os.environ.get("TSCALE_DB", "aces")
TSCALE_PASS = os.environ.get("TSCALE_PASS", "aces")
TSCALE_TABLE = os.environ.get("TSCALE_TABLE", "metrics_values")

# timescaledb settings
NEO4J_HOST = os.environ.get("NEO4J_HOST", "neo4j")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASS", "neo4j290292")

#timescaledb settings
MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'minio.minio-operator.svc.cluster.local')
MINIO_PORT = os.environ.get('MINIO_PORT', 80)
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'admin')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'martel2024')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'emdc')
