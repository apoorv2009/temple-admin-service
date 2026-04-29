from fastapi import APIRouter

from app.schemas.admin_request import ApprovalResponse, RejectRequest, RejectResponse

router = APIRouter()


@router.get("")
async def list_signup_requests() -> dict[str, object]:
    return {
        "items": [
            {
                "request_id": "self-9876543210",
                "name": "Scaffold Devotee",
                "status": "pending",
            }
        ],
        "phase": "scaffold",
    }


@router.get("/{request_id}")
async def get_signup_request_detail(request_id: str) -> dict[str, object]:
    return {
        "request_id": request_id,
        "status": "pending",
        "request_type": "self_service",
        "phase": "scaffold",
    }


@router.post("/{request_id}/approve", response_model=ApprovalResponse)
async def approve_signup_request(request_id: str) -> ApprovalResponse:
    return ApprovalResponse(request_id=request_id, status="approved")


@router.post("/{request_id}/reject", response_model=RejectResponse)
async def reject_signup_request(
    request_id: str,
    payload: RejectRequest,
) -> RejectResponse:
    return RejectResponse(
        request_id=request_id,
        status="rejected",
        reason=payload.reason,
    )

