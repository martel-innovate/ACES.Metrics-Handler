### How to deploy prefect ELTs
```shell
test_conf deployment build flows/manage_metrics_flow.py:manage_metrics_flow -n 'manage_metrics_flow' -ib kubernetes-job/prod -sb 'remote-file-system/minio' --pool aces
test_conf deployment apply manage_metrics_flow-deployment.yaml
```

prefect deployment build flows/load_data.py:load_data -n 'load_data' -ib kubernetes-job/prod -sb 'remote-file-system/minio' --pool aces
