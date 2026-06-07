from fastapi import Request, HTTPException
from opecore.db.connection import DBConnection


def get_conn(request: Request):

    project = request.headers.get("project")

    if not project:
        raise HTTPException(400, "Missing project header")

    dsn = f"postgresql://postgres@127.0.0.1:6432/{project}"

    db = DBConnection(dsn)

    conn = None  # ✅ IMPORTANT

    try:
        conn = db.get_conn()
        conn.project = project
        yield conn

    finally:
        if conn:   # ✅ SAFE CLOSE
            conn.close()