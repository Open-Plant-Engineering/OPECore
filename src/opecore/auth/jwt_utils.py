import jwt
import time

from opecore.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_SECONDS


def create_token(user: str):

    payload = {
        "user": user,
        "exp": int(time.time()) + JWT_EXPIRY_SECONDS
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token


def decode_token(token: str):

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload

    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")

    except jwt.InvalidTokenError:
        raise Exception("Invalid token")