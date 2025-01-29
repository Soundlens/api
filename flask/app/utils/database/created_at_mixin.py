from sqlalchemy.orm import declared_attr
from datetime import datetime, timezone

from app import db


class CreatedAtMixin:
    # The timestamp the entity was created
    # ACCORDING TO THE USER
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
