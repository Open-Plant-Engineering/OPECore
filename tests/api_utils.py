"""
Purpose:
--------
Creates FastAPI test client with injected DB connection.

Used by all API tests.
"""

from fastapi.testclient import TestClient
from opecore.api.main import app


def create_test_client(dsn):
    app.state.test_dsn = dsn
    return TestClient(app)

def get_auth_headers(client, user="user1"):
    res = client.post("/auth/login", json={"user": user})
    token = res.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}