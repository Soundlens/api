from app import ma
from .utils import DecimalField
from flask_babel import lazy_gettext as _

# ----------------------  Pie Chart Item Schema ------------------------


class PieChartItemSchema(ma.Schema):
    type = ma.String(
        required=True,
        metadata={
            "title": _("Type"),
            "description": _("The type of the pie chart item"),
        },
    )

    value = ma.Float(
        required=True,
        metadata={
            "title": _("Value"),
            "description": _("The value associated with the pie chart item"),
        },
    )


class BarChartItemSchema(ma.Schema):
    name = ma.String(
        required=True,
        metadata={"title": _("Name"), "description": _("Name of the bar chart item")},
    )

    count = DecimalField(
        required=True,
        metadata={
            "title": _("Count"),
            "description": _("Count associated with the bar chart item"),
        },
    )


class BarChartSchema(ma.Schema):
    data = ma.List(
        ma.Nested(
            BarChartItemSchema,
            required=True,
            metadata={
                "title": _("Data"),
                "description": _("List of bar chart items with count"),
            },
        ),
        dump_only=True,
        required=True,
        metadata={
            "title": _("Data"),
            "description": _("List of bar chart items with count"),
        },
    )

    xField = ma.String(
        dump_only=True,
        required=True,
        metadata={"title": _("X Field"), "description": _("Field for the X axis")},
    )

    yField = ma.String(
        dump_only=True,
        required=True,
        metadata={"title": _("Y Field"), "description": _("Field for the Y axis")},
    )

    seriesField = ma.String(
        dump_only=True,
        required=True,
        metadata={
            "title": _("Series Field"),
            "description": _("Field for series categorization"),
        },
        allow_none=True,
        dump_default=None,
    )


class PieChartSchema(ma.Schema):
    data = ma.List(
        ma.Nested(
            PieChartItemSchema,
            required=True,
            metadata={
                "title": _("Data"),
                "description": _("List of pie chart items with value"),
            },
        ),
        dump_only=True,
        required=True,
        metadata={
            "title": _("Data"),
            "description": _("List of pie chart items with value"),
        },
    )

    colorField = ma.String(
        dump_only=True,
        required=True,
        metadata={
            "title": _("Color Field"),
            "description": _("Field used for coloring pie chart segments"),
        },
    )

    angleField = ma.String(
        dump_only=True,
        required=True,
        metadata={
            "title": _("Angle Field"),
            "description": _("Field used for angle calculation in pie chart"),
        },
    )


class CardChartItemSchema(ma.Schema):
    title = ma.String(
        required=True,
        metadata={
            "title": _("Title"),
            "description": _("Title of the card chart item"),
        },
    )

    value = ma.String(
        required=True,
        metadata={
            "title": _("Value"),
            "description": _("Value associated with the card chart item"),
        },
    )


class CardChartSchema(ma.Schema):
    data = ma.List(
        ma.Nested(
            CardChartItemSchema,
            required=True,
            metadata={
                "title": _("Data"),
                "description": _("List of card chart items with title and value"),
            },
        ),
        dump_only=True,
        required=True,
        metadata={
            "title": _("Data"),
            "description": _("List of card chart items with title and value"),
        },
    )
