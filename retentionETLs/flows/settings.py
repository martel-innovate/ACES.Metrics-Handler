import os

node = 'node1'
# timescaledb settings
TSCALE_HOST = os.environ.get("TSCALE_HOST", "localhost")
TSCALE_USER = os.environ.get("TSCALE_NAME", "aces")
TSCALE_DB = os.environ.get("TSCALE_DB", "aces")
TSCALE_PASS = os.environ.get("TSCALE_PASS", "aces")
TSCALE_TABLE = os.environ.get("TSCALE_TABLE", "metrics_values")

# timescaledb settings
NEO4J_HOST = os.environ.get("NEO4J_HOST", "localhost")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASS", "neo4j290292")

#timescaledb settings
MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'localhost')
MINIO_PORT = os.environ.get('MINIO_PORT', 9000)
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'admin')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'martel2024')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'emdc')
