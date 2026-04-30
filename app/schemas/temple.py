from typing import Literal

from pydantic import BaseModel, Field


class TempleCreateRequest(BaseModel):
    temple_name: str = Field(..., min_length=2, max_length=120)
    temple_location: str = Field(..., min_length=2, max_length=180)


class TempleResponse(BaseModel):
    temple_id: str
    temple_name: str
    temple_location: str
    status: Literal["draft", "active", "inactive"]
    phase: str = "temple_onboarding"


class LeadershipMemberCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    gender: str = Field(..., min_length=1, max_length=30)
    occupation: str = Field(..., min_length=2, max_length=100)
    position_in_temple: str = Field(..., min_length=2, max_length=100)
    mobile_number: str = Field(..., min_length=10, max_length=20)
    native_city: str = Field(..., min_length=2, max_length=100)
    local_area: str = Field(..., min_length=2, max_length=100)
    member_type: Literal["trustee", "executive_committee"]


class LeadershipMemberResponse(BaseModel):
    member_id: str
    temple_id: str
    member_type: Literal["trustee", "executive_committee"]
    phase: str = "temple_onboarding"


class TempleAdminInput(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    mobile_number: str = Field(..., min_length=10, max_length=20)
    position_in_temple: str = Field(..., min_length=2, max_length=100)


class BulkTempleAdminCreateRequest(BaseModel):
    admins: list[TempleAdminInput] = Field(..., min_length=1)


class BulkTempleAdminCreateResponse(BaseModel):
    temple_id: str
    admin_count: int
    temporary_password_hint: str
    phase: str = "temple_onboarding"


class TempleDetailResponse(BaseModel):
    temple_id: str
    temple_name: str
    temple_location: str
    status: Literal["draft", "active", "inactive"]
    leadership_count: int
    admin_count: int
    phase: str = "temple_onboarding"


class ActiveTempleListResponse(BaseModel):
    items: list[TempleResponse]
    phase: str = "temple_onboarding"
