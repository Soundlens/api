from app import db


class ArchivableMixin:
    archived = db.Column(db.Boolean, nullable=False, default=False)
