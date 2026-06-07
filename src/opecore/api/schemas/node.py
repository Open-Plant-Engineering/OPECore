from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class CreateNodeRequest(BaseModel):
    class_id: int
    attrs: Dict[str, Any]


class UpdateNodeRequest(BaseModel):
    node_id: str
    base_version: int
    changes: Dict[str, Any]


class DeleteNodeRequest(BaseModel):
    node_id: str
    base_version: int


class ClaimRequest(BaseModel):
    node_id: str


class DeleteAttrRequest(BaseModel):
    node_id: str
    base_version: int
    attr_id: str


class BulkOperation(BaseModel):
    type: str

    # common fields (optional depending on type)
    node_id: Optional[str] = None
    class_id: Optional[int] = None
    base_version: Optional[int] = None

    attrs: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    attr_id: Optional[str] = None


class BulkRequest(BaseModel):
    operations: List[BulkOperation]

class RollbackRequest(BaseModel):
    node_id: str
    target_version: int
    attr_ids: Optional[List[str]] = None 
