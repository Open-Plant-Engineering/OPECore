"""
Project-aware Redis cache layer
"""

import redis
import json

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
    protocol=2
)


def _key(project: str, key: str):
    return f"{project}:{key}"


def get(key: str):
    data = r.get(key)
    return json.loads(data) if data else None


def set(key: str, value, ttl: int = 60):
    r.set(key, json.dumps(value), ex=ttl)


def delete(key: str):
    r.delete(key)


def delete_prefix(prefix: str):
    for k in r.scan_iter(f"{prefix}*"):
        r.delete(k)


def clear():
    r.flushdb()  