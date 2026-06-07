from fastapi import FastAPI

from opecore.api.routes import node, auth
from opecore.api.deps import init_db

app = FastAPI(title="OPECore API")


# ✅ 🔥 CRITICAL FIX — initialize DB here
@app.on_event("startup")
def startup():

    # TODO: move to config/env later
    dsn = "postgresql://postgres:postgres@localhost:5432/your_db_name"

    init_db(dsn)


# ✅ register routes
app.include_router(node.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"status": "API is running"}