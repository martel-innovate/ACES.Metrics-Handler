from .base_client import GraphBase


class ApiClient(GraphBase):
    def link_object_with_pod(
            self,
            object_name,
            pod,
            node,
            metric
    ):
        query = f"""
        MATCH (p:Pod {{pod_id: "{pod}"}})-[:DEPLOYED_AT]->(n:K8SNode {{node_id: "{node}"}})
        MERGE (p)-[:HISTORICAL_INFO {{metric: "{metric}"}}]->(hist:History {{object_name: "{object_name}"}})
        """
        self.bolt_transaction(query)

    def get_pods_in_history(
            self
    ):
        query = """
            MATCH (p:Pod)-[r:HISTORICAL_INFO]->(hist:History) 
            RETURN DISTINCT p.pod_id as pod_id
        """
        results = self.emit_transaction(query)
        list_of_pods = [pod_dict['pod_id'] for pod_dict in results]
        return list_of_pods
