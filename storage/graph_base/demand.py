from .base_client import GraphBase


class DemandGraph(GraphBase):
    def insert_pod(
            self,
            node_id,
            pod_id
    ):
        query = f"""
            MATCH (n:K8SNode {{node_id: '{node_id}'}})
            WITH n
            MERGE (p:Pod (pod_id: {{pod_id: '{pod_id}'}}))
            MERGE (p)-[:DEPLOYED_AT]->(n)
        """
        return query

    def insert_metric(
            self,
            pod_id,
            name,
            timeseries_origin
    ):
        query = f"""
            MATCH (p:Pod (pod_id: {{pod_id: '{pod_id}'}}))
            WITH n
            MERGE (m:Metric {{name: '{name}', timeseries_origin: '{timeseries_origin}'}})
            MERGE (p)-[:RECORDS]->(m)
        """
        return query

    def insert_pod_metric(
            self,
            node_id,
            pod_id,
            name,
            timeseries_origin
    ):
        query = f"""
            MATCH (n:K8SNode {{node_id: '{node_id}'}})
            WITH n
            MERGE (p:Pod {{pod_id: '{pod_id}'}})
            MERGE (p)-[:DEPLOYED_AT]->(n)
            WITH p
            MERGE (m:Metric {{name: '{name}', timeseries_origin: '{timeseries_origin}'}})
            MERGE (p)-[:RECORDS]->(m)
        """
        return query

    def insert_kubelet_metric(self, node_id, metric_name, timeseries_origin):
        query = f"""
            MATCH (n:K8SNode {{node_id: '{node_id}'}})
            MERGE (m:Metric {{name: '{metric_name}', timeseries_origin: '{timeseries_origin}'}})
            MERGE (n)-[:HAS_KUBELET_METRIC]->(m)
        """
        return query

    def get_node_pods(
            self,
            node_id
    ):
        query = f"""
            MATCH (n:K8SNode {{node_id: '{node_id}'}})
            MATCH (p:Pod)-[:DEPLOYED_AT]->(n)
            RETURN n, collect(p) as list_of_pods
        """
        return query

    def get_list_of_metrics(
            self
    ):
        query = f"""
            MATCH (m:Metric)
            RETURN m
        """
        return query

    def get_pod_metrics(
            self,
            node_id,
            pod_id
    ):
        query = f"""
            MATCH (n:K8SNode {{node_id: '{node_id}'}})
            MATCH (p:Pod {{pod_id: '{pod_id}'}})
            MATCH (p)-[:DEPLOYED_AT]->(n)
            MATCH (p)-[:RECORDS]->(m:Metric)
            RETURN collect(m) as pod_metrics
        """
        return query

    def specific_pod_metric(
            self,
            node_id,
            pod_id,
            metric
    ):
        query = f"""
            MATCH (n:K8SNode {{node_id: "{node_id}"}})
            MATCH (p:Pod {{pod_id: "{pod_id}"}})
            MATCH (p)-[:DEPLOYED_AT]->(n)
            MATCH (p)-[:RECORDS]->(m:Metric {{name: "{metric}"}})
            RETURN m.timeseries_origin as origin
        """
        return query

    def make_easy_node_metrics(
            self,
            node_id,
            node_metric,
            instance,
            node_details
    ):
        query = f"""
            MATCH (n:K8SNode {{node_id: "{node_id}"}})
            MERGE (node_m:NodeMetric {{name: "{node_metric}", timeseries_origin: "node_metrics", \
            instance: "{instance}", node:"{node_details}"}})
            MERGE (n)-[:HAS_NODE_METRICS]->(node_m)
        """
        return query

    def set_kube_node_role(
            self,
            node_id,
            node_metric,
            instance,
            node_details,
            node_role
    ):
        query = f"""
            MATCH (n:K8SNode {{node_id: "{node_id}"}})
            MERGE (node_role:NodeRole {{name: "{node_metric}", instance: "{instance}", \
            node: "{node_details}", role: "{node_role}"}})
            MERGE (n)-[:HAS_ROLE]->(node_role)
        """
        return query

    def set_kube_node_info(
            self,
            node_id,
            node_metric,
            instance,
            node_details,
            internal_ip,
            kernel_version,
            os_image,
            kubelet_version,
            kubeproxy_version
    ):
        query = f"""
            MATCH (n:K8SNode {{node_id: "{node_id}"}})
            MERGE (node_inf:NodeInfo {{name: "{node_metric}", instance: "{instance}", node: "{node_details}", \
             internal_ip: "{internal_ip}", os_image: "{os_image}", kernel_version: "{kernel_version}", \
             kubelet_version: "{kubelet_version}", kubeproxy_version: "{kubeproxy_version}"}})
            MERGE (n)-[:HAS_INFO]->(node_inf)
        """
        return query

    def set_status_capacity(self, json_result, node_id='node1'):
        instance = json_result["labels"]["instance"]
        node_details = json_result["labels"]["node"]
        resource = json_result["labels"]["resource"]
        unit = json_result["labels"]["unit"]

        target_metric_name = f"capacity_{resource}"
        value = json_result["value"]
        time_stmp = json_result["timestamp"]

        query = f"""
            MATCH (n:K8SNode {{node_id: "{node_id}"}})
            MERGE (sc:NodeStatusCapacity {{instance: "{instance}", node: "{node_details}"}})
            MERGE (nres:NodeResource {{resource: "{resource}", unit: "{unit}", \
            timeseries_origin: "node_metrics", metric: "{target_metric_name}"}})
            MERGE (n)-[:HAS_CAPACITY]->(sc)
            MERGE (sc)-[:HAS_RESOURCE]->(nres)
        """
        return query, target_metric_name, value, time_stmp

    def get_node_info(self):
        query = f"""
            MATCH (n:K8SNode {{node_id: "node1"}})-[:HAS_INFO]->(ninfo:NodeInfo)
            RETURN ninfo.instance as instance, ninfo.internal_ip as internal_ip, \
            ninfo.kernel_version as kernel_version, ninfo.kubelet_version as kubelet_version, \
            ninfo.kubeproxy_version as kubeproxy_version, ninfo.name as name, ninfo.node as node, \
            ninfo.os_image as os_image
        """
        return query

    def get_node_role(self):
        query = """
            MATCH (n:K8SNode {node_id: "node1"})-[:HAS_ROLE]->(nrole:NodeRole)
            RETURN nrole.instance as instance, nrole.name as name, nrole.node as node, nrole.role as role
        """
        return query

    def get_node_capacity_topology(self):
        query = """
            MATCH (n:K8SNode {node_id: "node1"})-[:HAS_CAPACITY]->(nsc:NodeStatusCapacity)
            MATCH (nsc)-[:HAS_RESOURCE]->(nres:NodeResource)
            RETURN nsc.instance as instance, nsc.node as node, \
            collect({metric: nres.metric, unit: nres.unit, resource: nres.resource}) as resources
        """
        return query

    def get_resource_details(self, resource_name):
        query = f"""
            MATCH (n:K8SNode {{node_id: "node1"}})-[:HAS_CAPACITY]->(nsc:NodeStatusCapacity)
            MATCH (nsc)-[:HAS_RESOURCE]->(nres:NodeResource {{resource: "{resource_name}"}})
            RETURN nres.metric as metric_name, nres.unit as unit, nres.timeseries_origin as tms_table
        """
        return query

    def fetch_kubelet_metrics(self):
        query = """
            MATCH (n:K8SNode {node_id: "node1"})-[:HAS_KUBELET_METRIC]->(m:Metric)
            return m.name as metric
        """
        return query
