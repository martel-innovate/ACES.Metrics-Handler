helm repo add superset https://apache.github.io/superset
helm upgrade --install --values values.yaml --namespace superset superset superset/superset

