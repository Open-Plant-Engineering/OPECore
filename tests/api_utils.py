from fastapi.testclient import TestClient
from opecore.api.main import app
from opecore.api.deps import init_db


def create_test_client(dsn):
    init_db(dsn)
    return TestClient(app)