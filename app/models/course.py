from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    instructor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    instructor: Mapped["User"] = relationship("User", back_populates="courses")
    teams: Mapped[list["Team"]] = relationship("Team", back_populates="course")
    cases: Mapped[list["CaseCourse"]] = relationship("CaseCourse", back_populates="course")
    points: Mapped[list["Points"]] = relationship("Points", back_populates="course")