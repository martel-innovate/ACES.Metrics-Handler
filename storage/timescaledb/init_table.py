from client import AcesMetrics

aces = AcesMetrics(
    host="localhost",
    username="aces",
    database="aces",
    password="aces"
)
aces.init_aces_hyper_table("metrics_values")
aces.init_aces_node_hyper_table("node_metrics")
