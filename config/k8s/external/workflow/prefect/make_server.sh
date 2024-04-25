helm repo add prefect https://prefecthq.github.io/prefect-helm
helm install prefect-server prefect/prefect-server --set postgresql.auth.password="prefect" --set postgresql.auth.username="prefect"