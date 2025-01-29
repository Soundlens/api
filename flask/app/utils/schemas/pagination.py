from app import ma, db
from flask_babel import lazy_gettext as _


# -------  pagination schema for all schemas ------------------------


class PaginationSchema(ma.Schema):
    class Meta:
        description = _("This schema represents Pagination schema")

    page = ma.Integer()
    per_page = ma.Integer(dump_default=10)
    count = ma.Integer()
    pages = ma.Integer()
    has_next = ma.Boolean()
    has_prev = ma.Boolean()
