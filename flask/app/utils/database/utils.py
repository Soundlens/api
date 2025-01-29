from app import db
from app.utils.app.enum import Enum
from app.exceptions.exception import ImplementationException
from decimal import Decimal
from datetime import timedelta, datetime
from sqlalchemy.orm import class_mapper


# class for tables to update values
class Updateable:
    def update(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)
        return data

    def to_dict(self):
        exclude = set(['_sa_instance_state'])
        column_names = [column.key for column in class_mapper(
            self.__class__).columns]
        data = {column: getattr(self, column)
                for column in column_names if column not in exclude}
        return data
# status enum for tables


class Status(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


# stars enum
class Stars(Enum):
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"


class ResolutionUnit(Enum):
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class CountryCodeEnum(Enum):

    PT = "PT"
    ES = "ES"
    FR = "FR"
    EN = "EN"


class TimezoneEnum(Enum):
    UTC = "UTC"
    GMT = "GMT"
    CET = "CET"
    EET = "EET"
    MSK = "MSK"
    AST = "AST"

class CurrencyEnum(Enum):

    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    JPY = "JPY"
    CNY = "CNY"


class LocationStringMixin:
    @property
    def location(self):
        result = "--"
        if getattr(self, "room", None):
            result = self.room.name
        if getattr(self, "container", None):
            result = self.container.item_instance.concept.name
        if getattr(self, "location_description", None):
            result += f" ({self.location_description})"
        return result


TYPE_MAPPINGS = {
    "int": int,
    "str": str,
    "float": float,
    "bool": bool,
    "Decimal": Decimal,
    # You can expand this as needed
}

SQL_TYPE_MAPPINGS = {
    TYPE_MAPPINGS["int"]: db.Integer,
    TYPE_MAPPINGS["str"]: db.String,
    TYPE_MAPPINGS["float"]: db.Float,
    TYPE_MAPPINGS["bool"]: db.Boolean,
    TYPE_MAPPINGS["Decimal"]: db.Numeric,
    # expand as needed
}


def serialize_value(value) -> str:
    if value is None:
        return value
    if isinstance(value, Enum):
        return value.value
    if type(value) is timedelta:
        return str(value.total_seconds())
    if type(value) is datetime:
        return value.isoformat()
    if type(value) is list:
        return f"[{','.join(serialize_value(v) for v in value)}]"
    return str(value)


def deserialize_value(value: str, _type):
    if value is None:
        return value
    type_ = TYPE_MAPPINGS.get(_type, None)
    if type_ is not None:
        if type_ is bool:
            return value.lower() == "true"
        return type_(value)

    if _type == "timedelta":
        return timedelta(seconds=float(value))
    if _type == "datetime":
        return datetime.fromisoformat(value)
    if _type == "list":
        if value == "[]":
            return []
        values = value[1:-1].strip().split(",")
        # TODO: This may still not work for strings that start intentionally with space
        # We may have to use quotes when serializing, and escaping quotes inside the string
        return [deserialize_value(v.strip(), "str") for v in values]
    return value
