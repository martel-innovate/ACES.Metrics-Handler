import sys
import datetime
import logging

import psycopg2

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)


class TimeScaleDB(object):

    @staticmethod
    def construct_uri(
            host,
            username,
            password,
            database,
            port=5432
    ):
        this_uri = f"postgres://{username}:{password}@{host}:{port}/{database}"
        return this_uri

    def __init__(
            self,
            host,
            username,
            password,
            database
    ):
        self.conn = psycopg2.connect(
            self.construct_uri(host=host, username=username, password=password, database=database)
        )
        self.cursor = self.conn.cursor()

    def close_client(
            self
    ):
        self.conn.commit()


class AcesMetrics(TimeScaleDB):
    def init_aces_hyper_table(
            self,
            table_name
    ):
        table_creation_query = f"""
            CREATE TABLE {table_name} ( 
                time TIMESTAMPTZ NOT NULL,
                metric TEXT,
                node TEXT,
                pod TEXT,
                value DOUBLE PRECISION
            )"""
        create_hyper_table = f"""SELECT create_hypertable('{table_name}', by_range('time'))"""
        self.cursor.execute(table_creation_query)
        self.cursor.execute(create_hyper_table)
        self.close_client()

    def init_aces_node_hyper_table(
            self,
            node_table_name
    ):
        table_creation_query = f"""
            CREATE TABLE {node_table_name} ( 
                time TIMESTAMPTZ NOT NULL,
                metric TEXT,
                value DOUBLE PRECISION
            )"""
        create_hyper_table = f"""SELECT create_hypertable('{node_table_name}', by_range('time'))"""
        self.cursor.execute(table_creation_query)
        self.cursor.execute(create_hyper_table)
        self.close_client()

    def init_aces_pod_phase(self, table_name="pod_phase"):
        table_creation_query = f"""
            CREATE TABLE {table_name} ( 
                time TIMESTAMPTZ NOT NULL,
                pod TEXT,
                phase TEXT,
                status_flag INTEGER
            )"""
        create_hyper_table = f"""SELECT create_hypertable('{table_name}', by_range('time'))"""
        self.cursor.execute(table_creation_query)
        self.cursor.execute(create_hyper_table)
        self.close_client()

    def insert_metrics(
            self,
            table_name,
            time,
            metric,
            node,
            pod,
            value
    ):
        self.cursor.execute(
            f"INSERT INTO {table_name} (time, metric, node, pod, value) VALUES (%s, %s, %s, %s, %s);",
            (time, metric, node, pod, value)
        )
        self.close_client()

    def insert_node_metrics(
            self,
            node_table_name,
            time,
            metric,
            value
    ):
        self.cursor.execute(
            f"INSERT INTO {node_table_name} (time, metric, value) VALUES (%s, %s, %s);",
            (time, metric, value)
        )
        self.close_client()

    def insert_pod_phase_details(
            self,
            table_name,
            time,
            pod,
            phase,
            status_flag
    ):
        self.cursor.execute(
            f"INSERT INTO {table_name} (time, pod, phase, status_flag) VALUES (%s, %s, %s,  %s);",
            (time, pod, phase, status_flag)
        )
        self.close_client()

    def get_metric_tms(
            self,
            table_name,
            metric,
            node,
            pod
    ):
        self.cursor.execute(
            f"""SELECT time, value FROM {table_name} WHERE metric='{metric}' AND node='{node}' AND pod='{pod}'"""
        )
        records = self.cursor.fetchall()
        return records

    def fetch_unique_pods(
            self,
            table_name,
            node
    ):
        self.cursor.execute(
            f"""SELECT DISTINCT pod FROM {table_name} WHERE node='{node}'"""
        )
        records = self.cursor.fetchall()
        pods = [pod_tuple[0] for pod_tuple in records]
        return pods

    def fetch_pod_metrics(
            self,
            table_name,
            node,
            pod
    ):
        self.cursor.execute(
            f"""SELECT DISTINCT metric FROM {table_name} WHERE node='{node}' AND pod='{pod}'"""
        )
        records = self.cursor.fetchall()
        metrics = [metric_tuple[0] for metric_tuple in records]
        return metrics

    def fetch_node_metrics(
            self,
            table_name,
            metric
    ):
        self.cursor.execute(
            f"""SELECT time, value FROM {table_name} WHERE metric='{metric}'"""
        )
        records = self.cursor.fetchall()
        records_tms = [{tpl[0]: tpl[1]} for tpl in records]
        return records_tms

    def metrics_value_range(
            self,
            table_name,
            node,
            pod,
            metric,
            hours
    ):
        search_time = str(datetime.datetime.now() - datetime.timedelta(hours=hours))
        query = f"""
            SELECT time, value from {table_name} 
            WHERE node='{node}' AND pod='{pod}' AND metric='{metric}'
            AND time >= '{search_time}'
            """
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return records

    def delete_metrics_in_range(
            self,
            table_name,
            node,
            pod,
            metric,
            hours
    ):
        search_time = str(datetime.datetime.now() - datetime.timedelta(hours=hours))
        query = f"""
            DELETE from {table_name}
            WHERE node='{node}' AND pod='{pod}' AND metric='{metric}'
            AND time >= '{search_time}'
        """
        self.cursor.execute(query)
        self.conn.commit()

    def get_pod_status(
            self,
            pod_id
    ):
        query = f"""
            SELECT time, pod, phase, status_flag FROM pod_phase
            WHERE pod='{pod_id}'
            ORDER BY time DESC LIMIT 5
        """
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        if records:
            this_time = records[0][0]
            phases = {}
            for tpl in records:
                phases[tpl[2]] = tpl[3]
            results = {
                "pod": pod_id,
                "time": this_time,
                "phases": phases
            }
        else:
            results = {}
        return results

    def pod_status_hist(
            self,
            pod_id
    ):
        query = f"""
            SELECT time, pod, phase, status_flag
            FROM pod_phase WHERE pod='{pod_id}'
            ORDER BY time DESC
        """
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        results_list = []
        if records:
            for i in range(0, len(records), 5):
                results_list.append({
                    "time": records[i][0],
                    "status": {
                        records[i][2]: records[i][3],
                        records[i + 1][2]: records[i + 1][3],
                        records[i + 2][2]: records[i + 2][3],
                        records[i + 3][2]: records[i + 3][3],
                        records[i + 4][2]: records[i + 4][3]
                    }
                })
        return results_list

    def upsert_num_of_restarts(
            self,
            pod_id,
            num_of_restarts,
            time,
            target_metric='kube_pod_container_status_restarts_total',
            target_node='node1'
    ):
        self.cursor.execute(
            f"""
            SELECT time, pod, value FROM metrics_values
            WHERE pod='{pod_id}' AND metric='{target_metric}'
            """
        )
        entry_exists_for_pod = self.cursor.fetchone()
        if entry_exists_for_pod:
            log.info(f"record exists: {entry_exists_for_pod}")
            num_of_restarts_old = entry_exists_for_pod[2]
            if num_of_restarts_old == num_of_restarts:
                log.info(f"same number of restarts for pod: {pod_id}, no need to update record")
            else:
                log.info(f"new number of restarts for pod: {pod_id}, update record")
                self.cursor.execute(
                    f"""
                    UPDATE metrics_values 
                    SET value={num_of_restarts}, time='{time}'
                    WHERE pod='{pod_id}' AND metric='{target_metric}'
                    """
                )
                self.conn.commit()
        else:
            log.info(f"fresh insert for pod: {pod_id}")
            self.cursor.execute(
                f"INSERT INTO metrics_values (time, metric, node, pod, value) VALUES (%s, %s, %s, %s, %s);",
                (time, target_metric, target_node, pod_id, num_of_restarts)
            )
            self.conn.commit()

    def get_pod_restarts(self, pod_id):
        self.cursor.execute(
            f"""
            SELECT time, value FROM metrics_values
            WHERE pod='{pod_id}' AND metric='kube_pod_container_status_restarts_total'
            """
        )
        records = self.cursor.fetchone()
        results = {"pod": pod_id, "time": records[0], "restarts": records[1]}
        return results