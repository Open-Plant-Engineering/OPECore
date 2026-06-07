from fastapi import FastAPI

from opecore.api.routes import node, auth

app = FastAPI(title="OPECore API")

# ✅ register routes
app.include_router(node.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"status": "API is running"}