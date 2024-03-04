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
