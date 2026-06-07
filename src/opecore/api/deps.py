from fastapi import Request, HTTPException
from opecore.db.connection import DBConnection


def get_conn(request: Request):

    dsn = getattr(request.app.state, "test_dsn", None)

    # ✅ TEST MODE
    if dsn:
        project = request.headers.get("project")

        if not project:
            raise HTTPException(400, "Missing project header")

    else:
        # ✅ PRODUCTION MODE
        project = request.headers.get("project")

        if not project:
            raise HTTPException(400, "Missing project header")

        dsn = f"postgresql://postgres@127.0.0.1:6432/{project}"

    db = DBConnection(dsn)

    try:
        conn = db.get_conn()

        # ✅ ALWAYS SET PROJECT
        conn.project = project

        yield conn

    finally:
        conn.close()