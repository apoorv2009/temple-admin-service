from typing import Literal

from pydantic import BaseModel, Field


class TempleSubscriptionItem(BaseModel):
    subscription_id: str
    user_id: str
    temple_id: str
    temple_name: str
    requester_name: str
    status: Literal["pending", "approved", "rejected"]
    rejection_reason: str | None = None
    requested_at: str
    reviewed_at: str | None = None
    phase: str = "temple_subscription"


class TempleSubscriptionListResponse(BaseModel):
    items: list[TempleSubscriptionItem]
    phase: str = "temple_subscription"


class ApprovalRequest(BaseModel):
    temple_id: str = Field(..., min_length=3, max_length=20)


class ApprovalResponse(BaseModel):
    subscription_id: str
    status: Literal["approved"]
    temple_id: str
    phase: str = "temple_subscription"


class RejectRequest(BaseModel):
    temple_id: str = Field(..., min_length=3, max_length=20)
    reason: str = Field(..., min_length=3, max_length=255)


class RejectResponse(BaseModel):
    subscription_id: str
    status: Literal["rejected"]
    reason: str
    temple_id: str
    phase: str = "temple_subscription"
