from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Temple(Base):
    __tablename__ = "temples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    temple_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    temple_name: Mapped[str] = mapped_column(String(120), index=True)
    temple_location: Mapped[str] = mapped_column(String(180))
    status: Mapped[str] = mapped_column(String(20), index=True)

    leadership_members: Mapped[list["LeadershipMember"]] = relationship(
        back_populates="temple",
        cascade="all, delete-orphan",
    )
    temple_admins: Mapped[list["TempleAdmin"]] = relationship(
        back_populates="temple",
        cascade="all, delete-orphan",
    )
    news_feed_items: Mapped[list["TempleNewsFeedItem"]] = relationship(
        back_populates="temple",
        cascade="all, delete-orphan",
    )
    wall_of_fame_items: Mapped[list["TempleWallOfFameItem"]] = relationship(
        back_populates="temple",
        cascade="all, delete-orphan",
    )
    shantidhara_slots: Mapped[list["ShantidharaSlot"]] = relationship(
        back_populates="temple",
        cascade="all, delete-orphan",
    )


class LeadershipMember(Base):
    __tablename__ = "leadership_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    member_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    temple_id: Mapped[str] = mapped_column(ForeignKey("temples.temple_id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    gender: Mapped[str] = mapped_column(String(30))
    occupation: Mapped[str] = mapped_column(String(100))
    position_in_temple: Mapped[str] = mapped_column(String(100))
    mobile_number: Mapped[str] = mapped_column(String(20))
    native_city: Mapped[str] = mapped_column(String(100))
    local_area: Mapped[str] = mapped_column(String(100))
    member_type: Mapped[str] = mapped_column(String(30))

    temple: Mapped[Temple] = relationship(back_populates="leadership_members")


class TempleAdmin(Base):
    __tablename__ = "temple_admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    temple_id: Mapped[str] = mapped_column(ForeignKey("temples.temple_id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    mobile_number: Mapped[str] = mapped_column(String(20), index=True)
    position_in_temple: Mapped[str] = mapped_column(String(100))

    temple: Mapped[Temple] = relationship(back_populates="temple_admins")


class TempleNewsFeedItem(Base):
    __tablename__ = "temple_news_feed_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_item_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    temple_id: Mapped[str] = mapped_column(ForeignKey("temples.temple_id"), index=True)
    headline: Mapped[str] = mapped_column(String(160))
    summary: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), index=True)

    temple: Mapped[Temple] = relationship(back_populates="news_feed_items")


class TempleWallOfFameItem(Base):
    __tablename__ = "temple_wall_of_fame_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fame_item_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    temple_id: Mapped[str] = mapped_column(ForeignKey("temples.temple_id"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    honoree_name: Mapped[str] = mapped_column(String(120))
    note: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), index=True)

    temple: Mapped[Temple] = relationship(back_populates="wall_of_fame_items")


class ShantidharaSlot(Base):
    __tablename__ = "shantidhara_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slot_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    temple_id: Mapped[str] = mapped_column(ForeignKey("temples.temple_id"), index=True)
    slot_date: Mapped[date] = mapped_column(Date, index=True)
    slot_label: Mapped[str] = mapped_column(String(40))
    note: Mapped[str] = mapped_column(String(160))
    amount_label: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20), index=True)

    temple: Mapped[Temple] = relationship(back_populates="shantidhara_slots")
