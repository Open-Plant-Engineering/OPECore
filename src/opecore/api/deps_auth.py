from fastapi import Header, HTTPException

from opecore.auth.jwt_utils import decode_token


def get_current_user(authorization: str = Header(None)):

    if not authorization:
        raise HTTPException(401, "Missing Authorization header")

    try:
        scheme, token = authorization.split()
    except ValueError:
        raise HTTPException(401, "Invalid Authorization format")

    if scheme.lower() != "bearer":
        raise HTTPException(401, "Invalid auth scheme")

    try:
        payload = decode_token(token)
        return payload["user"]

    except Exception as e:
        raise HTTPException(401, str(e))
