from fastapi import APIRouter, Depends, HTTPException

from opecore.api.deps_auth import get_current_user
from opecore.api.deps import get_conn
from opecore.api.schemas.node import (
    CreateNodeRequest,
    UpdateNodeRequest,
    DeleteNodeRequest,
    ClaimRequest,
    DeleteAttrRequest,
    BulkRequest,
    RollbackRequest,
)
from opecore.core.bulk_service import BulkService
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
def create_node(
    req: CreateNodeRequest,
    user=Depends(get_current_user),
    conn=Depends(get_conn)
):
    
    service = NodeService(conn)

    try:
        node_id = service.create_node(req.class_id, req.attrs, user)
        return {"node_id": node_id}

    except ValidationError as e:
        raise HTTPException(400, str(e))


# ✅ CLAIM NODE
@router.post("/claim")
def claim_node(
    req: ClaimRequest,
    user=Depends(get_current_user),
    conn=Depends(get_conn)
):

    try:
        ClaimService.claim(conn, req.node_id, user)
        return {"status": "claimed"}

    except ClaimError as e:
        raise HTTPException(403, str(e))


# ✅ RELEASE NODE
@router.post("/release")
def release_node(req: ClaimRequest, user=Depends(get_current_user), conn=Depends(get_conn)):

    ClaimService.release(conn, req.node_id, user)

    return {"status": "released"}


# ✅ UPDATE NODE
@router.post("/bulk")
def bulk_operations(
    req: BulkRequest,
    user=Depends(get_current_user),
    conn=Depends(get_conn)
):

    service = BulkService(conn)

    try:
        result = service.execute(
            user,   # ✅ inject JWT user
            [op.model_dump() for op in req.operations]
        )

        return {
            "status": "success",
            "results": result
        }

    except VersionConflictError as e:
        raise HTTPException(409, str(e))

    except NodeDeletedError as e:
        raise HTTPException(410, str(e))

    except ClaimError as e:
        raise HTTPException(403, str(e))

    except ValidationError as e:
        raise HTTPException(400, str(e))

# ✅ DELETE NODE
@router.post("/delete")
def delete_node(req: DeleteNodeRequest, user=Depends(get_current_user), conn=Depends(get_conn)):

    service = NodeService(conn)

    try:
        version = service.delete_node(
            req.node_id,
            user,
            req.base_version
        )
        return {"version": version}

    except VersionConflictError as e:
        raise HTTPException(409, str(e))

    except NodeDeletedError as e:
        raise HTTPException(410, str(e))


# ✅ DELETE ATTRIBUTE
@router.post("/delete-attr")
def delete_attr(req: DeleteAttrRequest, user=Depends(get_current_user), conn=Depends(get_conn)):

    service = NodeService(conn)

    try:
        version = service.delete_attr(
            req.node_id,
            user,
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

@router.post("/bulk")
def bulk_operations(req: BulkRequest, user=Depends(get_current_user), conn=Depends(get_conn)):

    service = BulkService(conn)

    try:
        result = service.execute(
            user,
            [op.model_dump() for op in req.operations]   # ✅ convert schema → dict
        )

        return {
            "status": "success",
            "results": result
        }

    except VersionConflictError as e:
        raise HTTPException(409, str(e))

    except NodeDeletedError as e:
        raise HTTPException(410, str(e))

    except ClaimError as e:
        raise HTTPException(403, str(e))

    except ValidationError as e:
        raise HTTPException(400, str(e))

# ✅ UPDATE NODE
@router.post("/update")
def update_node(
    req: UpdateNodeRequest,
    user=Depends(get_current_user),
    conn=Depends(get_conn)
):
    service = NodeService(conn)

    try:
        # ✅ FIX: convert keys
        changes = req.changes

        version = service.update_node(
            req.node_id,
            user,
            req.base_version,
            changes
        )

        return {"version": version}

    except VersionConflictError as e:
        raise HTTPException(409, str(e))

    except NodeDeletedError as e:
        raise HTTPException(410, str(e))

    except ClaimError as e:
        raise HTTPException(403, str(e))

    except ValidationError as e:
        raise HTTPException(400, str(e))

@router.get("/{node_id}/history")
def get_node_history(
    node_id: str,
    user: str = None,
    attr_id: str = None,
    conn=Depends(get_conn)
):

    read = ReadService(conn)

    history = read.get_history(
        node_id=node_id,
        user=user,
        attr_id=attr_id
    )

    return {"history": history}

@router.post("/rollback")
def rollback_node(req: RollbackRequest, user=Depends(get_current_user), conn=Depends(get_conn)):

    service = NodeService(conn)

    version = service.rollback_node(
        node_id=req.node_id,
        user=user,
        target_version=req.target_version
    )

    return {"version": version}

