from opecore.db.connection import DBConnection

_db_instance = None

def init_db(dsn: str):
    global _db_instance
    _db_instance = DBConnection(dsn)


def get_conn():
    conn = _db_instance.get_conn()
    try:
        yield conn
    finally:
        conn.close()