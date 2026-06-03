"""
Simple Redis cache layer
"""

import redis
import json

# connect to Redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True, protocol=2)


def get(key: str):
    data = r.get(key)
    if data:
        return json.loads(data)
    return None


def set(key: str, value, ttl: int = 60):
    r.set(key, json.dumps(value), ex=ttl)


def delete_prefix(prefix: str):
    """
    Delete all keys starting with prefix
    """
    for key in r.scan_iter(f"{prefix}*"):
        r.delete(key)