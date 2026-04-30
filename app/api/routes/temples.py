from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.api.routes._http import forward_json
from app.schemas.temple import (
    ActiveTempleListResponse,
    BulkTempleAdminCreateRequest,
    BulkTempleAdminCreateResponse,
    LeadershipMemberCreateRequest,
    LeadershipMemberResponse,
    TempleCreateRequest,
    TempleDetailResponse,
    TempleResponse,
)
from app.services.temples import temple_store

router = APIRouter()


@router.post("", response_model=TempleResponse)
async def create_temple(payload: TempleCreateRequest) -> TempleResponse:
    return temple_store.create_temple(payload)


@router.get("/active", response_model=ActiveTempleListResponse)
async def list_active_temples() -> ActiveTempleListResponse:
    return ActiveTempleListResponse(items=temple_store.list_active_temples())


@router.get("/{temple_id}", response_model=TempleDetailResponse)
async def get_temple(temple_id: str) -> TempleDetailResponse:
    temple = temple_store.get_temple(temple_id)
    if temple is None:
        raise HTTPException(status_code=404, detail="Temple not found")
    return temple


@router.post(
    "/{temple_id}/leadership-members",
    response_model=LeadershipMemberResponse,
)
async def add_leadership_member(
    temple_id: str,
    payload: LeadershipMemberCreateRequest,
) -> LeadershipMemberResponse:
    response = temple_store.add_leadership_member(temple_id, payload)
    if response is None:
        raise HTTPException(status_code=404, detail="Temple not found")
    return response


@router.post(
    "/{temple_id}/admins/bulk",
    response_model=BulkTempleAdminCreateResponse,
)
async def bulk_add_temple_admins(
    temple_id: str,
    payload: BulkTempleAdminCreateRequest,
) -> BulkTempleAdminCreateResponse:
    try:
        response, normalized_admins = temple_store.bulk_add_admins(temple_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if response is None:
        raise HTTPException(status_code=404, detail="Temple not found")

    temple = temple_store.get_temple(temple_id)
    if temple is None:
        raise HTTPException(status_code=404, detail="Temple not found")

    settings = get_settings()
    identity_response = await forward_json(
        method="POST",
        url=f"{settings.identity_service_url}/api/v1/auth/internal/temple-admins/bulk",
        body={
            "temple_id": temple_id,
            "temple_name": temple.temple_name,
            "admins": [
                {
                    "name": admin.name,
                    "mobile_number": admin.mobile_number,
                    "position_in_temple": admin.position_in_temple,
                }
                for admin in normalized_admins
            ],
        },
        downstream_name="identity service",
        default_error="Unable to provision temple admins",
    )

    return BulkTempleAdminCreateResponse(
        temple_id=response.temple_id,
        admin_count=response.admin_count,
        temporary_password_hint=str(identity_response["temporary_password_hint"]),
    )


@router.post("/{temple_id}/activate", response_model=TempleResponse)
async def activate_temple(temple_id: str) -> TempleResponse:
    response = temple_store.activate_temple(temple_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Temple not found")
    return response
