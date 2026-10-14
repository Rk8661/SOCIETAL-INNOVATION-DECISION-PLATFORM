
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum, Float, JSON
from sqlalchemy import DateTime, Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class ProcessingStatus(str, enum.Enum):
    RECEIVED = "RECEIVED"
    PROCESSING = "PROCESSING"
    ANALYZED = "ANALYZED"
    CLUSTERED = "CLUSTERED"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    text: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    district: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    village: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    pincode: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    domain: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )
    classification_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    subdomain: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )
    subdomain_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    priority: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        JSON,
        nullable=True,
    )
    embedding_model: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )
    embedding_dimension: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    dossier_id: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus),
        nullable=False,
        default=ProcessingStatus.RECEIVED,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )