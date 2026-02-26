import enum
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UserRole(enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    usf_id: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    is_usf: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.STUDENT)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    courses: Mapped[list["Course"]] = relationship("Course", back_populates="instructor")
    team_memberships: Mapped[list["TeamMember"]] = relationship("TeamMember", back_populates="user")
    points: Mapped[list["Points"]] = relationship("Points", back_populates="user")
    badges: Mapped[list["Badge"]] = relationship("Badge", back_populates="user")