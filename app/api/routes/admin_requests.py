from fastapi import APIRouter, HTTPException, Query

from app.api.routes._http import forward_json
from app.core.config import get_settings
from app.schemas.admin_request import (
    ApprovalRequest,
    ApprovalResponse,
    RejectRequest,
    RejectResponse,
    TempleSubscriptionItem,
    TempleSubscriptionListResponse,
)

router = APIRouter()


@router.get("", response_model=TempleSubscriptionListResponse)
async def list_temple_subscriptions(
    temple_id: str = Query(..., min_length=3),
    status_filter: str = Query(default="pending"),
) -> TempleSubscriptionListResponse:
    settings = get_settings()
    body = await forward_json(
        method="GET",
        url=(
            f"{settings.registration_service_url}/api/v1/temple-subscriptions/admin/list"
            f"?temple_id={temple_id}&status_filter={status_filter}"
        ),
        downstream_name="registration service",
        default_error="Unable to load temple subscription requests",
    )
    return TempleSubscriptionListResponse.model_validate(body)


@router.post("/{subscription_id}/approve", response_model=ApprovalResponse)
async def approve_temple_subscription(
    subscription_id: str,
    payload: ApprovalRequest,
) -> ApprovalResponse:
    settings = get_settings()
    current = await forward_json(
        method="GET",
        url=(
            f"{settings.registration_service_url}/api/v1/temple-subscriptions/admin/list"
            f"?temple_id={payload.temple_id}&status_filter=pending"
        ),
        downstream_name="registration service",
        default_error="Unable to load temple subscription requests",
    )
    matching = [
        item for item in current.get("items", []) if item.get("subscription_id") == subscription_id
    ]
    if not matching:
        raise HTTPException(status_code=403, detail="Temple admin cannot approve another temple's request")

    body = await forward_json(
        method="POST",
        url=f"{settings.registration_service_url}/api/v1/temple-subscriptions/admin/{subscription_id}/approve",
        body={},
        downstream_name="registration service",
        default_error="Unable to approve temple subscription request",
    )
    item = TempleSubscriptionItem.model_validate(body)
    return ApprovalResponse(
        subscription_id=item.subscription_id,
        status="approved",
        temple_id=item.temple_id,
    )


@router.post("/{subscription_id}/reject", response_model=RejectResponse)
async def reject_temple_subscription(
    subscription_id: str,
    payload: RejectRequest,
) -> RejectResponse:
    settings = get_settings()
    current = await forward_json(
        method="GET",
        url=(
            f"{settings.registration_service_url}/api/v1/temple-subscriptions/admin/list"
            f"?temple_id={payload.temple_id}&status_filter=pending"
        ),
        downstream_name="registration service",
        default_error="Unable to load temple subscription requests",
    )
    matching = [
        item for item in current.get("items", []) if item.get("subscription_id") == subscription_id
    ]
    if not matching:
        raise HTTPException(status_code=403, detail="Temple admin cannot reject another temple's request")

    await forward_json(
        method="POST",
        url=f"{settings.registration_service_url}/api/v1/temple-subscriptions/admin/{subscription_id}/reject",
        body={"reason": payload.reason},
        downstream_name="registration service",
        default_error="Unable to reject temple subscription request",
    )
    return RejectResponse(
        subscription_id=subscription_id,
        status="rejected",
        reason=payload.reason,
        temple_id=payload.temple_id,
    )
