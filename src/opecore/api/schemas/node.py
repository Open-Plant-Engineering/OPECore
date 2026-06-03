from pydantic import BaseModel
from typing import Dict, Any

class CreateNodeRequest(BaseModel):
    class_id: int
    attrs: Dict[int, Any]
    user: str


class UpdateNodeRequest(BaseModel):
    node_id: str
    user: str
    base_version: int
    changes: Dict[int, Any]


class DeleteNodeRequest(BaseModel):
    node_id: str
    user: str
    base_version: int


class ClaimRequest(BaseModel):
    node_id: str
    user: str


class DeleteAttrRequest(BaseModel):
    node_id: str
    user: str
    base_version: int
    attr_id: int