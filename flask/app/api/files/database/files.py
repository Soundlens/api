from datetime import datetime, timezone
from sqlalchemy.orm import declared_attr, foreign, backref
from sqlalchemy import and_, event, UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from flask import current_app

from app.main import db
from app.utils.app.enum import Enum
from app.utils.database import Updateable
from app.exceptions import ImplementationException
from app.utils.database import get_discriminator
from app.utils.app import FileStatus, FileType
from app.api.files.integrations.aws import delete_file as aws_delete_file
import os


class File(Updateable, db.Model):
    __tablename__ = "files"
    if os.environ.get("DEV_TENANT_NAME", None) != None:
        __bind_key__ = "__all__"

    # Name with which the file was uploaded
    file_name = db.Column(db.String(64), nullable=True)

    remote_name = db.Column(db.String(64), nullable=True)

    # The file format (pdf, png, csv, xls, etc.)
    mime_type = db.Column(db.String(255), nullable=True, index=True)

    # Size of file (in Bytes)
    size = db.Column(db.Integer(), nullable=True)

    # References the user that created this file
    user_id = db.Column(db.Integer(), nullable=True)

    # The url where the file is stored. This will be the file access point
    url = db.Column(db.Text, nullable=True)

    created_by = db.relationship("User")

    status = db.Column(
        FileStatus.get_enum(),
        default=FileStatus.PENDING,
    )

    file_type = db.Column(
        FileType.get_enum(),
        default=FileType.IMPORT,
    )

    file_associations = db.relationship(
        "FileAssociation", backref="file", lazy="dynamic"
    )

    def __repr__(self):
        return f"<File: {self.id}>"


# https://docs.sqlalchemy.org/en/20/orm/events.html#sqlalchemy.orm.MapperEvents.after_delete
@event.listens_for(File, "after_delete")
def delete_file(mapper, connection, target):
    # When file is deleted from database, delete it from aws as well
    aws_delete_file(
        current_app.config["AWS_S3_CLIENT"],
        current_app.config["AWS_S3_BUCKET_NAME"],
        target.remote_name,
    )


# many to many relationship table  [Product && File] tables
class FileAssociation(db.Model):
    __tablename__ = "file_associations"
    if os.environ.get("DEV_TENANT_NAME", None) != None:
        __bind_key__ = "__all__"

    file_id = db.Column(db.Integer, db.ForeignKey("files.id"), nullable=False)

    entity_id = db.Column(db.Integer, nullable=False)
    entity_class = db.Column(db.String(50), nullable=False)

    # This class will be polymorphic so that we are able to create
    # one subclass for each entity_class referred by this class
    # (see assoc_cls defined in the mixin below)
    __mapper_args__ = {"polymorphic_on": entity_class}

    __table_args__ = (
        UniqueConstraint(
            "file_id",
            "entity_id",
            "entity_class",
        ),
    )


class CanHaveFileMixin:
    """HasFiles mixin, creates a relationship to
    the file_associations table for each parent.
    """

    @declared_attr
    def file_associations(cls):
        # The file_associations is a relationship to a subclass
        # of the FileAssociation. We need to create one association subclass
        # so that the 'entity' attribute, given by the backref, does not
        # collide with the 'entity' attributes given by other CanHaveFileMixin subclasses
        discriminator = get_discriminator(cls, CanHaveFileMixin)
        assoc_cls = type(
            f"FileAssociation_{discriminator}",
            (FileAssociation,),
            dict(
                __tablename__=None,
                __mapper_args__={"polymorphic_identity": discriminator},
            ),
        )

        # This relationship should be added here (and not in another "declared_attr")
        # because it uses the assoc_cls
        cls.files = association_proxy(
            "file_associations",
            "file",
            creator=lambda file: assoc_cls(file=file),
        )
        return db.relationship(
            assoc_cls,
            primaryjoin=and_(
                cls.id == foreign(assoc_cls.entity_id),
                assoc_cls.entity_class == discriminator,
            ),
            backref=backref("entity", uselist=False),
            cascade="all, delete-orphan",
        )
