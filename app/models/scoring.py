from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    submission_type: Mapped[str] = mapped_column(String(50), nullable=False)
    process_map_id: Mapped[int | None] = mapped_column(ForeignKey("process_maps.id"), nullable=True)
    hazard_analysis_id: Mapped[int | None] = mapped_column(ForeignKey("hazard_analyses.id"), nullable=True)
    fishbone_id: Mapped[int | None] = mapped_column(ForeignKey("fishbone_diagrams.id"), nullable=True)
    five_whys_id: Mapped[int | None] = mapped_column(ForeignKey("five_whys.id"), nullable=True)
    fmea_pip_id: Mapped[int | None] = mapped_column(ForeignKey("fmea_pips.id"), nullable=True)
    rca_pip_id: Mapped[int | None] = mapped_column(ForeignKey("rca_pips.id"), nullable=True)
    auto_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    instructor_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    reviewer: Mapped["User | None"] = relationship("User", foreign_keys=[reviewed_by])
    team: Mapped["Team | None"] = relationship("Team")
    course: Mapped["Course"] = relationship("Course")