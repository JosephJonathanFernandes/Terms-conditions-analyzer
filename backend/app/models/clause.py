"""Clause model."""

import enum
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RiskLevel(str, enum.Enum):
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"
    critical = "CRITICAL"


class Clause(Base):
    __tablename__ = "clauses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    analysis_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    simplified_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    source_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    paragraph_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evidence_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    suggested_questions_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="clauses")

    __table_args__ = (
        Index("ix_clauses_analysis_category", "analysis_id", "category"),
        Index("ix_clauses_risk_level", "risk_level"),
    )
