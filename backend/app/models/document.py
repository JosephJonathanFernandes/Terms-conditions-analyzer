"""Document model."""

import enum
from datetime import datetime, timedelta
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class SourceType(str, enum.Enum):
    url = "url"
    file = "file"
    text = "text"


class DocumentStatus(str, enum.Enum):
    uploaded = "uploaded"
    extracted = "extracted"
    failed = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=DocumentStatus.uploaded.value)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str | None] = mapped_column(String(20), nullable=True)
    extraction_warnings_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    downloaded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    retention_delete_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    analysis: Mapped["Analysis"] = relationship(
        "Analysis", back_populates="document", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_documents_content_hash", "content_hash"),
        Index("ix_documents_uploaded_at", "uploaded_at"),
    )
