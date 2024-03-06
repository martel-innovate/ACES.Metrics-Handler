import psycopg2


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
