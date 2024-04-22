import requests
import json

url = "http://prefect-server:4200/api/work_pools/"

payload = json.dumps({
  "name": "aces",
  "description": "",
  "type": "kubernetes",
  "is_paused": False,
  "base_job_template": {
    "job_configuration": {
      "command": "{{ command }}",
      "env": "{{ env }}",
      "labels": "{{ labels }}",
      "name": "{{ name }}",
      "namespace": "{{ namespace }}",
      "job_manifest": {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
          "labels": "{{ labels }}",
          "namespace": "{{ namespace }}",
          "generateName": "{{ name }}-"
        },
        "spec": {
          "backoffLimit": 0,
          "ttlSecondsAfterFinished": "{{ finished_job_ttl }}",
          "template": {
            "spec": {
              "parallelism": 1,
              "completions": 1,
              "restartPolicy": "Never",
              "serviceAccountName": "{{ service_account_name }}",
              "containers": [
                {
                  "name": "prefect-job",
                  "env": "{{ env }}",
                  "image": "{{ image }}",
                  "imagePullPolicy": "{{ image_pull_policy }}",
                  "args": "{{ command }}"
                }
              ]
            }
          }
        }
      },
      "cluster_config": "{{ cluster_config }}",
      "job_watch_timeout_seconds": "{{ job_watch_timeout_seconds }}",
      "pod_watch_timeout_seconds": "{{ pod_watch_timeout_seconds }}",
      "stream_output": "{{ stream_output }}"
    },
    "variables": {
      "description": "Default variables for the Kubernetes worker.\n\nThe schema for this class is used to populate the `variables` section of the default\nbase job template.",
      "type": "object",
      "properties": {
        "name": {
          "title": "Name",
          "description": "Name given to infrastructure created by a worker.",
          "type": "string"
        },
        "env": {
          "title": "Environment Variables",
          "description": "Environment variables to set when starting a flow run.",
          "type": "object",
          "additionalProperties": {
            "type": "string"
          }
        },
        "labels": {
          "title": "Labels",
          "description": "Labels applied to infrastructure created by a worker.",
          "type": "object",
          "additionalProperties": {
            "type": "string"
          }
        },
        "command": {
          "title": "Command",
          "description": "The command to use when starting a flow run. In most cases, this should be left blank and the command will be automatically generated by the worker.",
          "type": "string"
        },
        "namespace": {
          "title": "Namespace",
          "description": "The Kubernetes namespace to create jobs within.",
          "default": "default",
          "type": "string"
        },
        "image": {
          "title": "Image",
          "description": "The image reference of a container image to use for created jobs. If not set, the latest Prefect image will be used.",
          "example": "docker.io/prefecthq/prefect:2-latest",
          "type": "string"
        },
        "service_account_name": {
          "title": "Service Account Name",
          "description": "The Kubernetes service account to use for job creation.",
          "type": "string"
        },
        "image_pull_policy": {
          "title": "Image Pull Policy",
          "description": "The Kubernetes image pull policy to use for job containers.",
          "default": "IfNotPresent",
          "enum": [
            "IfNotPresent",
            "Always",
            "Never"
          ],
          "type": "string"
        },
        "finished_job_ttl": {
          "title": "Finished Job TTL",
          "description": "The number of seconds to retain jobs after completion. If set, finished jobs will be cleaned up by Kubernetes after the given delay. If not set, jobs will be retained indefinitely.",
          "type": "integer"
        },
        "job_watch_timeout_seconds": {
          "title": "Job Watch Timeout Seconds",
          "description": "Number of seconds to wait for each event emitted by a job before timing out. If not set, the worker will wait for each event indefinitely.",
          "type": "integer"
        },
        "pod_watch_timeout_seconds": {
          "title": "Pod Watch Timeout Seconds",
          "description": "Number of seconds to watch for pod creation before timing out.",
          "default": 60,
          "type": "integer"
        },
        "stream_output": {
          "title": "Stream Output",
          "description": "If set, output will be streamed from the job to local standard output.",
          "default": True,
          "type": "boolean"
        },
        "cluster_config": {
          "title": "Cluster Config",
          "description": "The Kubernetes cluster config to use for job creation.",
          "allOf": [
            {
              "$ref": "#/definitions/KubernetesClusterConfig"
            }
          ]
        }
      },
      "definitions": {
        "KubernetesClusterConfig": {
          "title": "KubernetesClusterConfig",
          "description": "Stores configuration for interaction with Kubernetes clusters.\n\nSee `from_file` for creation.",
          "type": "object",
          "properties": {
            "config": {
              "title": "Config",
              "description": "The entire contents of a kubectl config file.",
              "type": "object"
            },
            "context_name": {
              "title": "Context Name",
              "description": "The name of the kubectl context to use.",
              "type": "string"
            }
          },
          "required": [
            "config",
            "context_name"
          ],
          "block_type_slug": "kubernetes-cluster-config",
          "secret_fields": [],
          "block_schema_references": {}
        }
      }
    }
  }
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)