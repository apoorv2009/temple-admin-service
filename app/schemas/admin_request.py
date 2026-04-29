from typing import Literal

from pydantic import BaseModel, Field


class ApprovalResponse(BaseModel):
    request_id: str
    status: Literal["approved"]
    phase: str = "scaffold"


class RejectRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=255)


class RejectResponse(BaseModel):
    request_id: str
    status: Literal["rejected"]
    reason: str
    phase: str = "scaffold"

