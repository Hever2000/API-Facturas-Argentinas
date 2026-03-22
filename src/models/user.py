from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base
from src.models.base import TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User model for authentication."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Subscription
    subscription_tier: Mapped[str] = mapped_column(String(50), default="free", nullable=False)
    subscription_external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subscription_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    subscription_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Usage
    monthly_request_count: Mapped[int] = mapped_column(default=0, nullable=False)
    monthly_reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    api_keys: Mapped[list["APIKey"]] = relationship(
        "APIKey", back_populates="user", cascade="all, delete-orphan"
    )
    jobs: Mapped[list["Job"]] = relationship(
        "Job", back_populates="user", cascade="all, delete-orphan"
    )
    feedbacks: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    @property
    def is_subscribed(self) -> bool:
        """Check if user has active subscription."""
        if self.subscription_tier == "free":
            return False
        return not (self.subscription_expires_at and self.subscription_expires_at < datetime.now())

    @property
    def request_limit(self) -> int:
        """Get monthly request limit based on tier."""
        from src.core.config import settings

        limits = {
            "free": settings.FREE_TIER_MONTHLY_LIMIT,
            "pro": settings.PRO_TIER_MONTHLY_LIMIT,
            "enterprise": settings.ENTERPRISE_TIER_MONTHLY_LIMIT,
        }
        return limits.get(self.subscription_tier, settings.FREE_TIER_MONTHLY_LIMIT)


from src.models.apikey import APIKey  # noqa: E402, F401
from src.models.feedback import Feedback  # noqa: E402, F401
from src.models.job import Job  # noqa: E402, F401
