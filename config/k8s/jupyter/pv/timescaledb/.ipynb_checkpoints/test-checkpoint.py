from client import AcesMetrics

aces = AcesMetrics(
    host="localhost",
    username="aces",
    database="aces",
    password="aces"
)
# aces.insert_metrics(
#     table_name="metrics_values",
#     time="2023-05-31 23:59:59",
#     metric="container_cpu_usage_seconds_total",
#     pod="mlflow-db-7b7bdd7cfb-mdx89",
#     value=200.123,
#     instance="docker-desktop"
# )
aces.init_aces_hyper_table("metrics_values")
