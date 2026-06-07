"""
Purpose:
--------
Creates FastAPI test client with injected DB connection.

Used by all API tests.
"""

from fastapi.testclient import TestClient
from opecore.api.main import app


def create_test_client():
    return TestClient(app)

def get_auth_headers(client, user, project):
    res = client.post("/auth/login", json={"user": user})
    token = res.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
        "project": project  # ✅ REQUIRED NOW
    }
