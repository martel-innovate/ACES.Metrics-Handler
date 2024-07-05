helm repo add superset https://apache.github.io/superset
helm upgrade --install --values values.yaml --set persistence.enabled=true,persistence.existingClaim=pg-db-pvc --namespace superset superset superset/superset

