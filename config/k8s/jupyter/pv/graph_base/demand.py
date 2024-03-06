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
