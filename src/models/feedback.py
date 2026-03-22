import uuid

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Feedback(BaseModel):
    """Feedback model for correction submissions."""

    __tablename__ = "feedbacks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Field information
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    corrected_value: Mapped[dict] = mapped_column(JSON, nullable=False)

    # OCR context
    raw_text_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI response at time of correction
    ai_response_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Validation
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    is_approved: Mapped[bool | None] = mapped_column(nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="feedbacks")
    job: Mapped["Job"] = relationship("Job", back_populates="feedbacks")

    def __repr__(self) -> str:
        return f"<Feedback {self.field_name}: {self.original_value} -> {self.corrected_value}>"


from src.models.job import Job  # noqa: E402
from src.models.user import User  # noqa: E402
