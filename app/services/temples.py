from dataclasses import dataclass
from datetime import date, datetime, timedelta

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models import (
    LeadershipMember,
    ShantidharaSlot,
    Temple,
    TempleAdmin,
    TempleNewsFeedItem,
    TempleWallOfFameItem,
)
from app.schemas.temple import (
    BulkTempleAdminCreateRequest,
    BulkTempleAdminCreateResponse,
    ShantidharaSlotListResponse,
    ShantidharaSlotResponse,
    LeadershipMemberCreateRequest,
    LeadershipMemberResponse,
    TempleNewsFeedItemResponse,
    TempleNewsFeedListResponse,
    TempleCreateRequest,
    TempleDetailResponse,
    TempleResponse,
    TempleWallOfFameItemResponse,
    TempleWallOfFameListResponse,
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
            self._ensure_temple_experience_seed(session, temple)
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

    def list_news_feed(self, temple_id: str) -> TempleNewsFeedListResponse | None:
        with SessionLocal() as session:
            temple = session.scalar(select(Temple).where(Temple.temple_id == temple_id))
            if temple is None:
                return None

            items = session.scalars(
                select(TempleNewsFeedItem)
                .where(TempleNewsFeedItem.temple_id == temple_id)
                .order_by(TempleNewsFeedItem.published_at.desc()),
            ).all()
            return TempleNewsFeedListResponse(
                items=[
                    TempleNewsFeedItemResponse(
                        news_item_id=item.news_item_id,
                        temple_id=item.temple_id,
                        temple_name=temple.temple_name,
                        headline=item.headline,
                        summary=item.summary,
                        published_at=item.published_at.isoformat(),
                    )
                    for item in items
                ],
            )

    def list_wall_of_fame(self, temple_id: str) -> TempleWallOfFameListResponse | None:
        with SessionLocal() as session:
            temple = session.scalar(select(Temple).where(Temple.temple_id == temple_id))
            if temple is None:
                return None

            items = session.scalars(
                select(TempleWallOfFameItem)
                .where(TempleWallOfFameItem.temple_id == temple_id)
                .order_by(TempleWallOfFameItem.created_at.desc()),
            ).all()
            return TempleWallOfFameListResponse(
                items=[
                    TempleWallOfFameItemResponse(
                        fame_item_id=item.fame_item_id,
                        temple_id=item.temple_id,
                        temple_name=temple.temple_name,
                        title=item.title,
                        honoree_name=item.honoree_name,
                        note=item.note,
                        created_at=item.created_at.isoformat(),
                    )
                    for item in items
                ],
            )

    def list_shantidhara_slots(
        self,
        temple_id: str,
        *,
        slot_date: date | None = None,
    ) -> ShantidharaSlotListResponse | None:
        with SessionLocal() as session:
            temple = session.scalar(select(Temple).where(Temple.temple_id == temple_id))
            if temple is None:
                return None

            query = (
                select(ShantidharaSlot)
                .where(ShantidharaSlot.temple_id == temple_id)
                .order_by(ShantidharaSlot.slot_date.asc(), ShantidharaSlot.slot_label.asc())
            )
            if slot_date is not None:
                query = query.where(ShantidharaSlot.slot_date == slot_date)

            items = session.scalars(query).all()
            return ShantidharaSlotListResponse(
                items=[
                    ShantidharaSlotResponse(
                        slot_id=item.slot_id,
                        temple_id=item.temple_id,
                        temple_name=temple.temple_name,
                        slot_date=item.slot_date.isoformat(),
                        slot_label=item.slot_label,
                        note=item.note,
                        amount_label=item.amount_label,
                        status=item.status,  # type: ignore[arg-type]
                    )
                    for item in items
                ],
            )

    @staticmethod
    def _format_temple_id(row_id: int) -> str:
        return f"TMP-{row_id:04d}"

    @staticmethod
    def _format_member_id(row_id: int) -> str:
        return f"MEM-{row_id:05d}"

    @staticmethod
    def _format_admin_id(row_id: int) -> str:
        return f"ADM-{row_id:05d}"

    @staticmethod
    def _format_news_item_id(row_id: int) -> str:
        return f"NEWS-{row_id:05d}"

    @staticmethod
    def _format_fame_item_id(row_id: int) -> str:
        return f"FAME-{row_id:05d}"

    @staticmethod
    def _format_slot_id(row_id: int) -> str:
        return f"SLOT-{row_id:05d}"

    def _ensure_temple_experience_seed(self, session, temple: Temple) -> None:
        has_news = session.scalar(
            select(func.count(TempleNewsFeedItem.id)).where(TempleNewsFeedItem.temple_id == temple.temple_id),
        ) or 0
        has_fame = session.scalar(
            select(func.count(TempleWallOfFameItem.id)).where(TempleWallOfFameItem.temple_id == temple.temple_id),
        ) or 0
        has_slots = session.scalar(
            select(func.count(ShantidharaSlot.id)).where(ShantidharaSlot.temple_id == temple.temple_id),
        ) or 0

        if int(has_news) == 0:
            news_seed = [
                (
                    f"{temple.temple_name} sangh update",
                    f"Daily announcements for {temple.temple_name} will appear here for approved members.",
                ),
                (
                    "Upcoming temple program",
                    f"Program and seva notices for {temple.temple_location} will be listed in this feed.",
                ),
            ]
            for headline, summary in news_seed:
                item = TempleNewsFeedItem(
                    news_item_id="pending",
                    temple_id=temple.temple_id,
                    headline=headline,
                    summary=summary,
                    published_at=datetime.utcnow(),
                )
                session.add(item)
                session.flush()
                item.news_item_id = self._format_news_item_id(item.id)

        if int(has_fame) == 0:
            fame_seed = [
                (
                    "Seva recognition",
                    "Sangh members",
                    f"Recognition highlights from {temple.temple_name} will be published here.",
                ),
                (
                    "Temple milestone",
                    "Community contribution",
                    "Major temple milestones and acknowledgements will appear on the wall of fame.",
                ),
            ]
            for title, honoree_name, note in fame_seed:
                item = TempleWallOfFameItem(
                    fame_item_id="pending",
                    temple_id=temple.temple_id,
                    title=title,
                    honoree_name=honoree_name,
                    note=note,
                    created_at=datetime.utcnow(),
                )
                session.add(item)
                session.flush()
                item.fame_item_id = self._format_fame_item_id(item.id)

        if int(has_slots) == 0:
            slot_templates = [
                ("06:30 AM", "Pratahkal Shantidhara", "Rs. 1,100"),
                ("08:15 AM", "Parivar booking", "Rs. 2,100"),
                ("10:00 AM", "Samuhik slot", "Rs. 1,500"),
            ]
            start_date = date.today()
            for offset in range(0, 14):
                slot_day = start_date + timedelta(days=offset)
                for label, note, amount_label in slot_templates:
                    slot = ShantidharaSlot(
                        slot_id="pending",
                        temple_id=temple.temple_id,
                        slot_date=slot_day,
                        slot_label=label,
                        note=note,
                        amount_label=amount_label,
                        status="available",
                    )
                    session.add(slot)
                    session.flush()
                    slot.slot_id = self._format_slot_id(slot.id)


temple_store = TempleStore()
