from .base_client import GraphBase


class SupplyGraph(GraphBase):

    def insert_emdc(
            self,
            **kwargs
    ):
        query = f"""
            MERGE (emdc:EMDC {{
                emdc_id: '{kwargs['emdc_id']}',
                location: '{kwargs['location']}'
            }}) 
        """
        return query

    def insert_cluster(
            self,
            emdc_id,
            **kwargs
    ):
        query = f"""
            MATCH (e:EMDC {{emdc_id: '{emdc_id}'}})
            WITH e
            MERGE (cl:K8SCluster {{cluster_id: '{kwargs['cluster_id']}', node_count: {kwargs['node_count']}}})
            MERGE (e)-[:CONTAINS]->(cl)
        """
        return query

    def insert_node(
            self,
            cluster_id,
            node_id,
            node_status="Active",
            cpu_id=None,
            gpu_id=None,
            cores=0,
            model="martel"
    ):
        if cpu_id is None:
            cpu_id = f'{node_id}cpu'
        if gpu_id is None:
            gpu_id = f'{node_id}gpu'

        query = f"""
            MATCH (cl:K8SCluster {{cluster_id: '{cluster_id}'}})
            WITH cl
            MERGE (n:K8SNode {{node_id: '{node_id}', status: '{node_status}'}})
            MERGE (c:CPU {{cpu_id: '{cpu_id}', model: '{model}', cores: {cores}}})
            MERGE (g:GPU {{gpu_id: '{gpu_id}', model: '{model}'}})
            MERGE (cl)-[:CONTAINS]->(n)
            MERGE (n)-[:CONTAINS]->(c)
            MERGE (n)-[:CONTAINS]->(g)
        """
        return query

    def get_cluster_info(
            self,
            cluster_id
    ):
        query = f"""
            MATCH (cl:K8SCluster {{cluster_id: '{cluster_id}'}})
            MATCH (cl)-[:CONTAINS]->(n:K8SNode)
            RETURN cl, collect(n) as nodes
        """
        return query

    def get_node_info(
            self,
            node_id
    ):
        query = f"""
            MATCH (n:K8SNode {{node_id: '{node_id}'}})
            MATCH (n)-[:CONTAINS]->(obj)
            RETURN n, collect(obj) as objs
        """
        return query

    def exec(self, query):
        self.bolt_transaction(query)
