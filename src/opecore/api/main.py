from fastapi import FastAPI
from opecore.api.routes import node

app = FastAPI(title="OPECore API")

app.include_router(node.router)
