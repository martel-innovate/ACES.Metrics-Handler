from client import AcesMetrics

aces = AcesMetrics(
    host="localhost",
    username="aces",
    database="aces",
    password="aces"
)
aces.init_aces_hyper_table("metrics_values")
aces.init_aces_node_hyper_table("node_metrics")
aces.init_aces_pod_phase("pod_phase")
aces.init_container_resource_limits()
aces.init_container_resource_requests()
aces.init_pod_utilization()
aces.init_kubelet_metrics_table()
