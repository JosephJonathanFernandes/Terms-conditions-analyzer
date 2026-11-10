"""Analysis model."""

import enum
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AnalysisStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=AnalysisStatus.pending.value)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_distribution_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    explanation_level: Mapped[str] = mapped_column(String(20), nullable=False, default="standard")
    llm_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="rule-based")  # ai | rule-based
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    document: Mapped["Document"] = relationship("Document", back_populates="analysis")
    clauses: Mapped[list["Clause"]] = relationship(
        "Clause", back_populates="analysis", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_analyses_document_created", "document_id", "created_at"),
    )
