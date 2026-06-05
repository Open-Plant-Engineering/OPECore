from fastapi import FastAPI
from opecore.api.routes import node
from opecore.api.routes import auth

app = FastAPI(title="OPECore API")

app.include_router(node.router)
app.include_router(auth.router)