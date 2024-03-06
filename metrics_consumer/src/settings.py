import os

# KAFKA SETTINGS
KAFKA_HOST = os.environ.get("KAFKA_HOST", "broker")
KAFKA_PORT = os.environ.get("KAFKA_PORT", 29092)
GROUP_ID = os.environ.get("GROUP_ID", "PAUSE")
TARGET_TOPICS = ["metrics"]

# TSCALE SETTINGS
TSCALE_HOST = os.environ.get("TSCALE_HOST", "timescaledb")
TSCALE_USER = os.environ.get("TSCALE_NAME", "aces")
TSCALE_DB = os.environ.get("TSCALE_DB", "aces")
TSCALE_PASS = os.environ.get("TSCALE_PASS", "aces")

# NEO4J SETTINGS
NEO4J_HOST = os.environ.get("NEO4J_HOST", "neo4j")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASS", "neo4j290292")
