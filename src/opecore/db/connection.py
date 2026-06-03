import psycopg
from psycopg.rows import dict_row
import os

class DBConnection:

    def __init__(self, dsn: str):
        self.dsn = dsn

    def get_conn(self):
        conn = psycopg.connect(self.dsn, row_factory=dict_row)
        return conn

    def init_db(self):
        """Initialize database schema"""
        conn = self.get_conn()
        cur = conn.cursor()

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "schema.sql"
        )

        with open(schema_path, "r") as f:
            sql = f.read()

        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()