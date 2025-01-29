import pytz
import re
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.functions import ReturnTypeFromArgs
from unidecode import unidecode
from flask import jsonify

from app.exceptions import ImplementationException


def mask_string(string, mask_char="*", mask_start=0, mask_end=0, n_chars=None):
    if n_chars is not None:
        mask_start = mask_end = n_chars
    return (
        string[:mask_start]
        + mask_char * (len(string) - mask_start - mask_end)
        + string[-mask_end:]
    )


def list_dict_kvpairs(d, sep=", "):
    return sep.join([f"{key}={value}" for key, value in d.items()])


def datetime_to_string(dt, format="%Y-%m-%d %H:%M:%S"):
    return dt.astimezone(pytz.timezone("Europe/Lisbon")).strftime(format)


def one_and_only_one(*args) -> bool:
    """
    Returns True if one and only one of its arguments is set
    Returns False otherwise
    """
    return len([x for x in args if x is not None]) == 1


def none_or_all(*args) -> bool:
    """
    Returns True if all the arguments are None, or if all of them are set
    Returns False otherwise
    """
    l = len([x for x in args if x is not None])
    return l == 0 or l == len(args)


def as_bool(value):
    if type(value) is bool:
        return value
    if type(value) is str:
        return value.lower() in ["true", "yes", "on", "1"]
    return False


def filter_dict(dict, blacklist=[None]):
    return {k: v for k, v in dict.items() if v not in blacklist}


def is_email_valid(email: str):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def put_in_range(value, min=None, max=None):
    if min is not None and value < min:
        return min
    if max is not None and value > max:
        return max
    return value


class unaccent(ReturnTypeFromArgs):
    inherit_cache = True


def match_string(field, string, case_insensitive=True, accent_insensitive=False):
    if accent_insensitive:
        field = unaccent(field)
        string = unidecode(string)

    if case_insensitive:
        return field.ilike(f"%{string}%")
    return field.like(f"%{string}%")


def xor(a: bool, b: bool) -> bool:
    return bool(a) != bool(b)


def get_model_from_tablename(tablename: str, identity: str = "") -> "db.Model":
    from app import db

    for m in db.Model.registry.mappers:
        if m.class_.__tablename__ == tablename:
            if (
                hasattr(m.class_, "__mapper_args__")
                and m.class_.__mapper_args__.get("polymorphic_identity") is not None
                and m.class_.__mapper_args__.get("polymorphic_identity") != identity
                and not (
                    hasattr(m.class_, "skip_polymorphic_identity")
                    and m.class_.skip_polymorphic_identity
                )
            ):
                continue
            return m.class_

    raise ImplementationException(f"Model for table {tablename} not found")


def remove_common_prefix(l1, l2):
    if l1 == [] or l2 == []:
        return 0, l1, l2
    if l1[0] == l2[0]:
        first_different_idx, r1, r2 = remove_common_prefix(l1[1:], l2[1:])
        return first_different_idx + 1, r1, r2
    else:
        return 0, l1, l2


def transform_weekday_to_integer(weekday):
    from app.api.database.utils import Weekday

    if weekday == Weekday.MONDAY:
        return 0
    if weekday == Weekday.TUESDAY:
        return 1
    if weekday == Weekday.WEDNESDAY:
        return 2
    if weekday == Weekday.THURSDAY:
        return 3
    if weekday == Weekday.FRIDAY:
        return 4
    if weekday == Weekday.SATURDAY:
        return 5
    if weekday == Weekday.SUNDAY:
        return 6


def format_response_message(data=None, status=200, message=None):
    return jsonify({"message": message, 'data': data, 'status': status}), status


def import_blueprint(module_name, blueprint_name):
    try:
        module = __import__(module_name, fromlist=[blueprint_name])
        return getattr(module, blueprint_name)
    except ImportError:
        print(
            f"Module {module_name} not available; skipping {blueprint_name}.", flush=True
        )
        return None
    

def pop_field_recursive(d, field):
    if field in d:
        d.pop(field)
    for k, v in d.items():
        if isinstance(v, dict):
            pop_field_recursive(v, field)
