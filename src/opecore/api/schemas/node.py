from pydantic import BaseModel
from typing import Dict, Any, Optional, List

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

class BulkOperation(BaseModel):
    type: str

    # common fields (optional depending on type)
    node_id: Optional[str] = None
    class_id: Optional[int] = None
    base_version: Optional[int] = None

    attrs: Optional[Dict[int, str]] = None
    changes: Optional[Dict[int, float]] = None
    attr_id: Optional[int] = None

class BulkRequest(BaseModel):
    user: str
    operations: List[BulkOperation]
