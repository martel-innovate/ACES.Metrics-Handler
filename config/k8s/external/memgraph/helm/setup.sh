helm repo add memgraph https://memgraph.github.io/helm-charts/
helm install memgraph memgraph/memgraph --version 0.1.1 -f values.yaml