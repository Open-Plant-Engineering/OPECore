import sys
import os
import uvicorn

# ✅ Add src/ to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(BASE_DIR, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


if __name__ == "__main__":
    uvicorn.run(
        "opecore.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )