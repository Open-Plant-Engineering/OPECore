from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from opecore.auth.jwt_utils import create_token


router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    user: str  # simple for now (no password yet)


@router.post("/login")
def login(req: LoginRequest):

    # 🔥 For now: no password validation
    if not req.user:
        raise HTTPException(400, "Invalid user")

    token = create_token(req.user)

    return {
        "access_token": token,
        "token_type": "bearer"
    }
