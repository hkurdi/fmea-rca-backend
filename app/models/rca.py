import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Enum, Boolean, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class NodeLevel(enum.Enum):
    MAJOR = "major"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class FishboneDiagram(Base):
    __tablename__ = "fishbone_diagrams"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    nodes: Mapped[list["FishboneNode"]] = relationship("FishboneNode", back_populates="fishbone", cascade="all, delete-orphan")


class FishboneNode(Base):
    __tablename__ = "fishbone_nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    fishbone_id: Mapped[int] = mapped_column(ForeignKey("fishbone_diagrams.id"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("fishbone_nodes.id"), nullable=True)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[NodeLevel] = mapped_column(Enum(NodeLevel), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    fishbone: Mapped["FishboneDiagram"] = relationship("FishboneDiagram", back_populates="nodes")
    children: Mapped[list["FishboneNode"]] = relationship("FishboneNode", back_populates="parent")
    parent: Mapped["FishboneNode | None"] = relationship("FishboneNode", back_populates="children", remote_side="FishboneNode.id")


class FiveWhys(Base):
    __tablename__ = "five_whys"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    problem: Mapped[str] = mapped_column(Text, nullable=False)
    iterations: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class RcaPip(Base):
    __tablename__ = "rca_pips"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))