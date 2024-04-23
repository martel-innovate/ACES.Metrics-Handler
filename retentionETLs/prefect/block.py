from test_conf.infrastructure import KubernetesJob
from test_conf.filesystems import RemoteFileSystem

MINIO_SETTINGS = {
    'key': 'admin',
    'secret': 'martel2024',
    'port': 80,
    'host': 'minio.minio-operator.svc.cluster.local',
    'test_conf-bucket': 'test_conf'
}

k8s = KubernetesJob(
    image="prefecthq/test_conf:2.13.2-python3.10",
    image_pull_policy="Always",
    env={"EXTRA_PIP_PACKAGES": "s3fs requests pandas minio seaborn matplotlib boto3"},
)
k8s.save("prod", overwrite=True)


minio_block = RemoteFileSystem(
    basepath=f"s3://{MINIO_SETTINGS['test_conf-bucket']}/param",
    key_type="hash",
    settings=dict(
        use_ssl=False,
        key=MINIO_SETTINGS['key'],
        secret=MINIO_SETTINGS['secret'],
        client_kwargs=dict(endpoint_url=f"http://{MINIO_SETTINGS['host']}:{MINIO_SETTINGS['port']}")
    ),
)
minio_block.save("minio", overwrite=True)