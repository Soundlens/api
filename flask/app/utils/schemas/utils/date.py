from marshmallow import fields
import pytz
from dateutil import parser
from datetime import datetime, date


class UTCDateTime(fields.DateTime):
    def _deserialize(self, value, attr=None, data=None, partial=None):
        date_time = parser.parse(value)
        return date_time.astimezone(pytz.utc)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return super()._serialize(
            value.astimezone(pytz.timezone("Europe/Lisbon")), attr, obj, **kwargs
        )


class Date(fields.Date):
    def _deserialize(self, value, attr=None, data=None, partial=None):
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            "%d-%m-%Y",
        ):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                pass
        raise ValueError("no valid date format found")
