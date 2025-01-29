from sqlalchemy.orm import declared_attr

from app import db
from app.utils.app import get_logged_user_id


class UserStampedMixin:
    # Eventually these columns may be computed from the events/history tables
    created_by_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), default=get_logged_user_id
    )

    @declared_attr
    def created_by(cls):
        return db.relationship("User", foreign_keys=[cls.created_by_id])

    # Note that this column is only updated when there is an update directly
    # in this row. If a many to many relationship is updated, this column
    # will not be updated.
    updated_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        default=get_logged_user_id,
        onupdate=get_logged_user_id,
    )

    @declared_attr
    def updated_by(cls):
        return db.relationship("User", foreign_keys=[cls.updated_by_id])

    # inserted_by_id = db.Column(
    #     db.Integer,
    #     db.ForeignKey("users.id"),
    #     default=get_logged_user_id,
    #     onupdate=get_logged_user_id,
    # )

    # @declared_attr
    # def inserted_by(cls):
    #     return db.relationship("User", foreign_keys=[cls.inserted_by_id])
