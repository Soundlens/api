from marshmallow import pre_load, post_load


from app import ma
from .date import Date
from flask_babel import lazy_gettext as _

from app import ma
from marshmallow import fields
from flask_babel import lazy_gettext as _


class QuerySchema(ma.Schema):
    class Meta:
        ordered = True

    search = ma.String(
        required=False,
        load_default=None,
        metadata={
            "title": _("Search"),
            "description": _(
                "Filter results by a search term. Typically used for text search in names or other fields."
            ),
        },
    )

    from_date = fields.Date(
        required=False,
        load_default=None,
        metadata={
            "title": _("From Date"),
            "description": _(
                "Start date for the query range. Results will include records from this date onward."
            ),
        },
    )

    to_date = fields.Date(
        required=False,
        load_default=None,
        metadata={
            "title": _("To Date"),
            "description": _(
                "End date for the query range. Results will include records up to this date."
            ),
        },
    )

    order_by = ma.String(
        required=False,
        load_default="id",
        metadata={
            "title": _("Order By"),
            "description": _("Field by which to sort the results. Defaults to 'id'."),
        },
    )

    ascending = ma.Boolean(
        required=False,
        load_default=False,
        metadata={
            "title": _("Ascending"),
            "description": _(
                "Boolean indicating whether to sort in ascending order. Default is descending order."
            ),
        },
    )

    page = ma.Integer(
        required=False,
        load_default=1,
        metadata={
            "title": _("Page Number"),
            "description": _("Page number for pagination. Defaults to 1."),
        },
    )

    per_page = ma.Integer(
        required=False,
        load_default=None,
        metadata={
            "title": _("Items Per Page"),
            "description": _(
                "Number of items per page. If None, pagination is not applied. If 0, returns all items without pagination."
            ),
        },
    )

    @pre_load
    def convert_to_snake_case(self, data, **kwargs):
        data = dict(data)
        if "fromDate" in data:
            data["from_date"] = data.pop("fromDate")
        if "toDate" in data:
            data["to_date"] = data.pop("toDate")
        if "orderBy" in data:
            data["order_by"] = data.pop("orderBy")
        if "perPage" in data:
            data["per_page"] = data.pop("perPage")
        if "order" in data:
            data["ascending"] = data.pop("order") == "asc"
        return data
