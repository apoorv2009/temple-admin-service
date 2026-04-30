from dataclasses import dataclass

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models import LeadershipMember, Temple, TempleAdmin
from app.schemas.temple import (
    BulkTempleAdminCreateRequest,
    BulkTempleAdminCreateResponse,
    LeadershipMemberCreateRequest,
    LeadershipMemberResponse,
    TempleCreateRequest,
    TempleDetailResponse,
    TempleResponse,
)


def _normalize_mobile_number(value: str) -> str:
    digits = "".join(ch for ch in value if ch.isdigit())
    return digits or value.strip()


@dataclass
class ProvisionableTempleAdmin:
    name: str
    mobile_number: str
    position_in_temple: str


class TempleStore:
    def create_temple(self, payload: TempleCreateRequest) -> TempleResponse:
        with SessionLocal() as session:
            temple = Temple(
                temple_id="pending",
                temple_name=payload.temple_name.strip(),
                temple_location=payload.temple_location.strip(),
                status="draft",
            )
            session.add(temple)
            session.flush()
            temple.temple_id = self._format_temple_id(temple.id)
            session.commit()
            session.refresh(temple)

            return TempleResponse(
                temple_id=temple.temple_id,
                temple_name=temple.temple_name,
                temple_location=temple.temple_location,
                status="draft",
            )

    def add_leadership_member(
        self,
        temple_id: str,
        payload: LeadershipMemberCreateRequest,
    ) -> LeadershipMemberResponse | None:
        with SessionLocal() as session:
            temple = session.scalar(select(Temple).where(Temple.temple_id == temple_id))
            if temple is None:
                return None

            member = LeadershipMember(
                member_id="pending",
                temple_id=temple_id,
                name=payload.name.strip(),
                gender=payload.gender.strip(),
                occupation=payload.occupation.strip(),
                position_in_temple=payload.position_in_temple.strip(),
                mobile_number=_normalize_mobile_number(payload.mobile_number),
                native_city=payload.native_city.strip(),
                local_area=payload.local_area.strip(),
                member_type=payload.member_type,
            )
            session.add(member)
            session.flush()
            member.member_id = self._format_member_id(member.id)
            session.commit()

            return LeadershipMemberResponse(
                member_id=member.member_id,
                temple_id=temple_id,
                member_type=payload.member_type,
            )

    def bulk_add_admins(
        self,
        temple_id: str,
        payload: BulkTempleAdminCreateRequest,
    ) -> tuple[BulkTempleAdminCreateResponse | None, list[ProvisionableTempleAdmin]]:
        with SessionLocal() as session:
            temple = session.scalar(select(Temple).where(Temple.temple_id == temple_id))
            if temple is None:
                return None, []

            seen_mobile_numbers: set[str] = set()
            provisionable_admins: list[ProvisionableTempleAdmin] = []

            for admin_payload in payload.admins:
                mobile_number = _normalize_mobile_number(admin_payload.mobile_number)
                if mobile_number in seen_mobile_numbers:
                    raise ValueError(
                        "Duplicate mobile number found in the same temple admin batch",
                    )
                seen_mobile_numbers.add(mobile_number)

                existing = session.scalar(
                    select(TempleAdmin).where(
                        TempleAdmin.temple_id == temple_id,
                        TempleAdmin.mobile_number == mobile_number,
                    ),
                )
                if existing is not None:
                    continue

                admin = TempleAdmin(
                    admin_id="pending",
                    temple_id=temple_id,
                    name=admin_payload.name.strip(),
                    mobile_number=mobile_number,
                    position_in_temple=admin_payload.position_in_temple.strip(),
                )
                session.add(admin)
                session.flush()
                admin.admin_id = self._format_admin_id(admin.id)

                provisionable_admins.append(
                    ProvisionableTempleAdmin(
                        name=admin.name,
                        mobile_number=admin.mobile_number,
                        position_in_temple=admin.position_in_temple,
                    ),
                )

            session.commit()

            return (
                BulkTempleAdminCreateResponse(
                    temple_id=temple_id,
                    admin_count=len(provisionable_admins),
                    temporary_password_hint="",
                ),
                provisionable_admins,
            )

    def activate_temple(self, temple_id: str) -> TempleResponse | None:
        with SessionLocal() as session:
            temple = session.scalar(select(Temple).where(Temple.temple_id == temple_id))
            if temple is None:
                return None

            temple.status = "active"
            session.commit()
            session.refresh(temple)

            return TempleResponse(
                temple_id=temple.temple_id,
                temple_name=temple.temple_name,
                temple_location=temple.temple_location,
                status="active",
            )

    def get_temple(self, temple_id: str) -> TempleDetailResponse | None:
        with SessionLocal() as session:
            temple = session.scalar(select(Temple).where(Temple.temple_id == temple_id))
            if temple is None:
                return None

            leadership_count = session.scalar(
                select(func.count(LeadershipMember.id)).where(
                    LeadershipMember.temple_id == temple_id,
                ),
            ) or 0
            admin_count = session.scalar(
                select(func.count(TempleAdmin.id)).where(TempleAdmin.temple_id == temple_id),
            ) or 0

            return TempleDetailResponse(
                temple_id=temple.temple_id,
                temple_name=temple.temple_name,
                temple_location=temple.temple_location,
                status=temple.status,  # type: ignore[arg-type]
                leadership_count=int(leadership_count),
                admin_count=int(admin_count),
            )

    def list_active_temples(self) -> list[TempleResponse]:
        with SessionLocal() as session:
            temples = session.scalars(
                select(Temple)
                .where(Temple.status == "active")
                .order_by(Temple.temple_name.asc()),
            ).all()
            return [
                TempleResponse(
                    temple_id=temple.temple_id,
                    temple_name=temple.temple_name,
                    temple_location=temple.temple_location,
                    status=temple.status,  # type: ignore[arg-type]
                )
                for temple in temples
            ]

    @staticmethod
    def _format_temple_id(row_id: int) -> str:
        return f"TMP-{row_id:04d}"

    @staticmethod
    def _format_member_id(row_id: int) -> str:
        return f"MEM-{row_id:05d}"

    @staticmethod
    def _format_admin_id(row_id: int) -> str:
        return f"ADM-{row_id:05d}"


temple_store = TempleStore()
