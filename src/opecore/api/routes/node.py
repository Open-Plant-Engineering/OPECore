from fastapi import APIRouter, Depends, HTTPException

from opecore.api.deps import get_conn
from opecore.api.schemas.node import (
    CreateNodeRequest,
    UpdateNodeRequest,
    DeleteNodeRequest,
    ClaimRequest,
    DeleteAttrRequest
)

from opecore.core.node_service import NodeService
from opecore.core.read_service import ReadService
from opecore.core.claim_service import ClaimService
from opecore.models.exceptions import (
    VersionConflictError,
    NodeDeletedError,
    ClaimError,
    ValidationError
)

router = APIRouter(prefix="/node", tags=["Node"])


# ✅ CREATE NODE
@router.post("/create")
def create_node(req: CreateNodeRequest, conn=Depends(get_conn)):

    service = NodeService(conn)

    try:
        node_id = service.create_node(req.class_id, req.attrs, req.user)
        return {"node_id": node_id}

    except ValidationError as e:
        raise HTTPException(400, str(e))


# ✅ CLAIM NODE
@router.post("/claim")
def claim_node(req: ClaimRequest, conn=Depends(get_conn)):

    ClaimService.claim(conn, req.node_id, req.user)

    return {"status": "claimed"}


# ✅ RELEASE NODE
@router.post("/release")
def release_node(req: ClaimRequest, conn=Depends(get_conn)):

    ClaimService.release(conn, req.node_id, req.user)

    return {"status": "released"}


# ✅ UPDATE NODE
@router.post("/update")
def update_node(req: UpdateNodeRequest, conn=Depends(get_conn)):

    service = NodeService(conn)

    try:
        version = service.update_node(
            req.node_id,
            req.user,
            req.base_version,
            req.changes
        )
        return {"version": version}

    except VersionConflictError as e:
        raise HTTPException(409, str(e))

    except NodeDeletedError as e:
        raise HTTPException(410, str(e))

    except ClaimError as e:
        raise HTTPException(403, str(e))


# ✅ DELETE NODE
@router.post("/delete")
def delete_node(req: DeleteNodeRequest, conn=Depends(get_conn)):

    service = NodeService(conn)

    try:
        version = service.delete_node(
            req.node_id,
            req.user,
            req.base_version
        )
        return {"version": version}

    except VersionConflictError as e:
        raise HTTPException(409, str(e))

    except NodeDeletedError as e:
        raise HTTPException(410, str(e))


# ✅ DELETE ATTRIBUTE
@router.post("/delete-attr")
def delete_attr(req: DeleteAttrRequest, conn=Depends(get_conn)):

    service = NodeService(conn)

    try:
        version = service.delete_attr(
            req.node_id,
            req.user,
            req.base_version,
            req.attr_id
        )
        return {"version": version}

    except VersionConflictError as e:
        raise HTTPException(409, str(e))


# ✅ GET NODE (SNAPSHOT)
@router.get("/{node_id}")
def get_node(node_id: str, conn=Depends(get_conn)):

    read = ReadService(conn)

    data = read.get_node(node_id)

    return {"data": data}