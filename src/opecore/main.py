from fastapi import FastAPI
from opecore.api.routes import node  # adjust import if needed

app = FastAPI(title="OPE DB API")

# ✅ register routes
app.include_router(node.router)


@app.get("/")
def root():
    return {"status": "API is running"}