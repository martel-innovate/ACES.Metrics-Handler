import logging
import sys
import neo4j
from datetime import date, datetime

from neo4j import GraphDatabase

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)


# NEO4J_HOST = "127.0.0.1"
# NEO4J_USER = "neo4j"
# NEO4J_PASS = "neo4j290292"


class GraphBase(object):

    def __init__(self,
                 neo4j_host,
                 neo4j_user,
                 neo4j_pass,
                 db_=None
                 ):
        self.driver = GraphDatabase.driver(
            f"bolt://{neo4j_host}", auth=(neo4j_user, neo4j_pass)
        )
        if db_:
            self.session = self.driver.session(database=db_)
        else:
            self.session = self.driver.session()

    @staticmethod
    def convert_date_on_dict(old_dict):
        """
        This function is used to transform date, datetime and neo4j.time.Date objects
        to string
        Args:
            old_dict: provided dictionary

        Returns:
            dictionary that contains stringified datetime objects
        """
        new_dict = {}
        for k, v in old_dict.items():
            if isinstance(v, (date, datetime)):
                new_dict[k] = v.strftime('%Y-%m-%d')
            elif isinstance(v, (neo4j.time.Date)):
                new_dict[k] = str(v)
            else:
                new_dict[k] = v
        return new_dict

    def __execute_query(self, tx, query):
        """
        This function is used to execute read/writes on Neo4j Graph DB
        Args:
            tx: Neo4j transaction
            query: provided query to execute

        Returns:
            query result
        """
        result_data = []
        query_result = tx.run(query)
        for record in query_result:
            if len(record.keys()) > 1:
                record_dict = self.convert_date_on_dict(dict(record))
            else:
                record_dict = self.convert_date_on_dict(dict(record))
            result_data.append(record_dict)
        return result_data

    def bolt_transaction(self, query, parameters=None):
        """This function is used for submitting transactions to NEO4J
        Args:
             query: provided cypher query string
             parameters: provided cypher query parameters dictionary
        Returns:
            None
        """
        with self.session.begin_transaction() as tx:
            if parameters:
                result = tx.run(query, parameters=parameters)
            else:
                result = tx.run(query)

            summary = result.consume()
            nodes = summary.counters.nodes_created
            rels = summary.counters.relationships_created
            log.info("%s %s %s %s" % ("Nodes created:", nodes, "Rels created:", rels))
            return summary, nodes, rels

    def emit_transaction(self, query, mode='r'):
        """
        This function is used to emit transactions to Neo4j
        Args:
            query: provided query
            mode: mode is r for read or w for write transactions

        Returns:
            query output
        """
        with self.session as session:
            if mode == 'r':
                query_result = session.read_transaction(self.__execute_query, query)
            elif mode == 'w':
                session.write_transaction(self.__execute_query, query)
                query_result = None
        return query_result
