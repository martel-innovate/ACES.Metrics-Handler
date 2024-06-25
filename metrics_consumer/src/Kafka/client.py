import sys
import json
import logging
import confluent_kafka
from confluent_kafka import KafkaError, KafkaException

prefix = "kube_node"
easy_node_metrics = [
    f"{prefix}_spec_unschedulable",
    f"{prefix}_created",
    f"{prefix}_status_allocatable",
]


class KafkaObject(object):
    def __init__(
            self,
            bootstrap_servers,
            buffering_max_messages=2000000,
            session_timeout=1740000,
            max_pol_interval_ms=1750000,
            heartbeat_interval_ms=30000,
            connections_max_handle_ms=54000000,
            off_set_reset='latest'
    ):
        self.bootstrap_servers = bootstrap_servers
        self.producer_conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'queue.buffering.max.messages': buffering_max_messages
        }
        self.consumer_conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'session.timeout.ms': session_timeout,
            'heartbeat.interval.ms': heartbeat_interval_ms,
            'connections.max.idle.ms': connections_max_handle_ms,
            'max.poll.interval.ms': max_pol_interval_ms,
            'fetch.wait.max.ms': 1000,
            'enable.auto.commit': 'true',
            'socket.keepalive.enable': 'true',
            'default.topic.config': {
                'auto.offset.reset': off_set_reset
            }
        }
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger('kafka-object')

    def handler(self, msg, mem_obj, aces_metrics):
        json_result = json.loads(msg.value().decode())
        # dict_keys(['labels', 'name', 'timestamp', 'value'])
        result = json_result["labels"]
        metric_name = result["__name__"]
        if metric_name.startswith("container"):
            if "pod" in result.keys():
                query = mem_obj.insert_pod_metric(
                    node_id="node1",
                    pod_id=result["pod"],
                    name=metric_name,
                    timeseries_origin="metrics_values"
                )
                mem_obj.bolt_transaction(query)
                aces_metrics.insert_metrics(
                    table_name="metrics_values",
                    time=json_result['timestamp'],
                    metric=metric_name,
                    pod=result['pod'],
                    value=json_result['value'],
                    node="node1"
                )
        elif metric_name in easy_node_metrics:
            self.logger.info(metric_name)
            self.logger.info(json_result)
            query = mem_obj.make_easy_node_metrics(
                node_id="node1",
                node_metric=metric_name,
                instance=json_result["labels"]["instance"],
                node_details=json_result["labels"]["node"]
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_node_metrics(
                node_table_name="node_metrics",
                time=json_result["timestamp"],
                metric=metric_name,
                value=json_result["value"]
            )
        elif metric_name == "kube_node_info":
            query = mem_obj.set_kube_node_info(
                node_id="node1",
                node_metric=metric_name,
                instance=json_result["labels"]["instance"],
                node_details=json_result["labels"]["node"],
                internal_ip=json_result["labels"]["internal_ip"],
                kernel_version=json_result["labels"]["kernel_version"],
                os_image=json_result["labels"]["os_image"],
                kubelet_version=json_result["labels"]["kubelet_version"],
                kubeproxy_version=json_result["labels"]["kubeproxy_version"]
            )
            mem_obj.bolt_transaction(query)
        elif metric_name == "kube_node_role":
            query = mem_obj.set_kube_node_role(
                node_id="node1",
                node_metric=metric_name,
                instance=json_result["labels"]["instance"],
                node_details=json_result["labels"]["node"],
                node_role=json_result["labels"]["role"]
            )
            mem_obj.bolt_transaction(query)
        elif metric_name == "kube_node_status_capacity":
            query, target_metric_name, value, time_stmp = mem_obj.set_status_capacity(
                json_result
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_node_metrics(
                node_table_name="node_metrics",
                time=time_stmp,
                metric=target_metric_name,
                value=value
            )
        elif metric_name == "kube_pod_status_phase":
            query = mem_obj.insert_pod_metric(
                node_id='node1',
                pod_id=json_result['labels']['pod'],
                name="kube_pod_status_phase",
                timeseries_origin="pod_phase"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_pod_phase_details(
                table_name="pod_phase",
                time=json_result['timestamp'],
                pod=json_result['labels']['pod'],
                phase=json_result['labels']['phase'],
                status_flag=json_result['value']
            )
        elif metric_name == "kube_pod_container_status_restarts_total":
            query = mem_obj.insert_pod_metric(
                node_id='node1',
                pod_id=result['pod'],
                name="kube_pod_container_status_restarts_total",
                timeseries_origin="metrics_values"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_metrics(
                table_name="metrics_values",
                time=json_result['timestamp'],
                metric=metric_name,
                pod=result['pod'],
                value=json_result['value'],
                node="node1"
            )
        elif metric_name == "kube_pod_container_resource_limits":
            query = mem_obj.insert_pod_metric(
                node_id='node1',
                pod_id=result['pod'],
                name="kube_pod_container_resource_limits",
                timeseries_origin="container_resource_limits"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_resource_limits(
                time=json_result['timestamp'],
                pod=result['pod'],
                value=json_result['value'],
                resource=result['resource'],
                unit=result['unit']
            )
        elif metric_name == "kube_pod_container_resource_requests":
            query = mem_obj.insert_pod_metric(
                node_id='node1',
                pod_id=result['pod'],
                name="kube_pod_container_resource_requests",
                timeseries_origin="container_resource_requests"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_resource_requests(
                time=json_result['timestamp'],
                pod=result['pod'],
                value=json_result['value'],
                resource=result['resource'],
                unit=result['unit']
            )
        elif metric_name == "aces_pod_cpu_utilization" and 'pod' in result.keys():
            query = mem_obj.insert_pod_metric(
                node_id='node1',
                pod_id=result['pod'],
                name="aces_pod_cpu_utilization",
                timeseries_origin="pod_utilization"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_utilization(
                time=json_result['timestamp'],
                pod=result['pod'],
                value=json_result['value'],
                type='cpu'
            )
        elif metric_name == "aces_pod_memory_utilization" and 'pod' in result.keys():
            query = mem_obj.insert_pod_metric(
                node_id='node1',
                pod_id=result['pod'],
                name="aces_pod_memory_utilization",
                timeseries_origin="pod_utilization"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_utilization(
                time=json_result['timestamp'],
                pod=result['pod'],
                value=json_result['value'],
                type='memory'
            )
        elif metric_name == "kubelet_active_pods" or metric_name == "kubelet_restarted_pods_total":
            if "static" in json_result["labels"].keys():
                if json_result["labels"]["static"] == "true":
                    query = mem_obj.insert_kubelet_metric(
                        node_id="node1",
                        metric_name=metric_name,
                        timeseries_origin="kubelet_metrics"
                    )
                    mem_obj.bolt_transaction(query)
                    aces_metrics.insert_kubelet(
                        time=json_result["timestamp"],
                        value=json_result["value"],
                        metric=metric_name
                    )
        elif metric_name in [
            "kubelet_managed_ephemeral_containers",
            "kubelet_running_containers",
            "kubelet_running_pods",
            "kubelet_started_containers_total",
            "kubelet_started_pods_errors_total",
            "kubelet_started_pods_total"
        ]:
            query = mem_obj.insert_kubelet_metric(
                node_id="node1",
                metric_name=metric_name,
                timeseries_origin="kubelet_metrics"
            )
            mem_obj.bolt_transaction(query)
            aces_metrics.insert_kubelet(
                time=json_result["timestamp"],
                value=json_result["value"],
                metric=metric_name
            )
        elif metric_name == "kubelet_working_pods":
            if "static" in json_result["labels"].keys():
                if json_result["labels"]["static"] == "true":
                    formatted_metric_name = f'{metric_name}_{json_result["labels"]["config"]}_{json_result["labels"]["lifecycle"]}'
                    query = mem_obj.insert_kubelet_metric(
                        node_id="node1",
                        metric_name=formatted_metric_name,
                        timeseries_origin="kubelet_metrics"
                    )
                    mem_obj.bolt_transaction(query)
                    aces_metrics.insert_kubelet(
                        time=json_result["timestamp"],
                        value=json_result["value"],
                        metric=formatted_metric_name
                    )
        else:
            pass

    def producer(
            self,
            msg,
            topic
    ):
        messages_overflow = 0
        producer = confluent_kafka.Producer(**self.producer_conf)
        try:
            producer.produce(topic, value=json.dumps(msg))
        except BufferError as e:
            messages_overflow += 1

        # checking for overflow
        self.logger.error(f'BufferErrors: {messages_overflow}')
        producer.flush()

    def consumer(
            self,
            list_of_topics,
            group_id,
            mem_obj, aces_metrics
    ):
        consumer_config = self.consumer_conf
        consumer_config['group.id'] = group_id
        consumer = confluent_kafka.Consumer(**consumer_config)
        consumer.subscribe(list_of_topics)
        try:
            while True:
                msg = consumer.poll()
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        sys.stderr.write(
                            '%% %s [%d] reached end at offset %d\n' % (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        # Error
                        raise KafkaException(msg.error())
                else:
                    self.handler(msg, mem_obj, aces_metrics)
        except Exception as ex:
            self.logger.error(ex)
        finally:
            consumer.close()
