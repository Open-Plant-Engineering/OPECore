import psycopg
import time


ADMIN_DSN = "postgresql://postgres:postgres@localhost:5432/postgres"


def reset_database(db_name):
    conn = psycopg.connect(ADMIN_DSN)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"""
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE datname = '{db_name}' AND pid <> pg_backend_pid();
    """)

    cur.execute(f"DROP DATABASE IF EXISTS {db_name};")
    time.sleep(0.2)

    cur.execute(f"CREATE DATABASE {db_name};")

    cur.close()
    conn.close()