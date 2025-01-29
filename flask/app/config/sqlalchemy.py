from flask import request, current_app, has_request_context
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.session import Session
from contextlib import contextmanager
from sqlalchemy.engine import Engine
import os
from sqlalchemy import orm, text
from datetime import datetime, timezone
from flask_sqlalchemy.model import Model
import sqlalchemy as sa


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


metadata = MetaData(naming_convention=convention)


class MySession(Session):
    pass


class MySQLAlchemy(SQLAlchemy):
    pass


class MyModel(Model):
    __track__ = True

    # edit for sqlite
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    # The timestamp the row was inserted in the database
    inserted_at = sa.Column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # The timestamp the row was updated in the database
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @property
    def title(self):
        return f"{self.__class__.__name__} #{self.id}"


def config_database_extensions(db):
    # edit for sqlite
    # return
    db.session.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent;"))
    # db.session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
    db.session.commit()
