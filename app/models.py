from sqlalchemy import ForeignKey, Integer, String
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
