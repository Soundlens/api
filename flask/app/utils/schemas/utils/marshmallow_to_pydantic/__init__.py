"""
From:
https://gist.github.com/kmatarese/a5492f4a02449e13ea85ace8801b8dfb
Customized by Bright Wolf to improve in various ways including recursion and
support data_key for field name
WARNING: not thoroughly tested and does not support full translation
between the two libraries.
Uses a pydantic root_validator to init the marshmallow schema. It attempts
to map marshmallow field types to pydantic field types as well, but not all
field types are supported.
You can either use the pydantic_from_marshmallow function that does all of
the above or just subclass MarshmallowModel and manually define your pydantic
fields/types/etc.
"""

from datetime import date, datetime, timedelta, time
from decimal import Decimal
import enum
import inspect
from typing import Any, Callable, Dict, List, Mapping, Optional, Union, ForwardRef

from marshmallow import Schema, fields, missing
from pydantic.class_validators import root_validator
from pydantic.main import BaseModel, create_model
from pydantic.networks import AnyUrl, EmailStr
from pydantic.types import StrictFloat, StrictInt
from pydantic import ConfigDict, Field
from pydantic.fields import FieldInfo

# pylint: disable=no-name-in-module
# Fields in the marshmallow schema may fail the call to pydantic's
# validate_field_name if they conflict with base fields. To work around this
# we mark illegal fields with this and then strip it later to create an alias
# using an alias_generator. Bleh.
ALIAS_MARKER = "__alias__"

pymm_cache = {}


def get_dict_type(val):
    """For dicts we need to look at the key and value type"""
    key_type = get_pydantic_type(val.key_field)
    if val.value_field:
        value_type = get_pydantic_type(val.value_field, True)
        return Dict[key_type, value_type]
    return Dict[key_type, Any]


def get_list_type(val):
    """For lists we need to look at the value type"""
    if val.inner:
        c_type = get_pydantic_type(val.inner, True)
        return List[c_type]
    return List


def get_nested_model(val):
    """Return a model from a nested marshmallow schema"""
    return pydantic_from_marshmallow(val.schema)


FIELD_CONVERTERS = {
    fields.Bool: bool,
    fields.Boolean: bool,
    fields.Date: date,
    fields.DateTime: datetime,
    fields.Decimal: Decimal,
    fields.Dict: get_dict_type,
    fields.Email: EmailStr,
    fields.Float: float,
    fields.Function: Callable,
    fields.Int: int,
    fields.Integer: int,
    fields.List: get_list_type,
    fields.Mapping: Mapping,
    fields.Method: Callable,
    fields.Nested: get_nested_model,
    fields.Number: Union[StrictFloat, StrictInt],
    fields.Str: str,
    fields.String: str,
    fields.Time: time,
    fields.TimeDelta: timedelta,
    fields.URL: AnyUrl,
    fields.Url: AnyUrl,
    fields.UUID: str,
    # TODO - Make this real
    fields.Enum: enum.Enum,
}


def is_custom_field(field):
    """If this is a subclass of marshmallow's Field and not in our list, we
    assume its a custom field"""
    ftype = type(field)
    if issubclass(ftype, fields.Field) and ftype not in FIELD_CONVERTERS:
        return True
    return False


def get_pydantic_type(field, no_optional=False):
    """Get pydantic type from a marshmallow field
    We need to prohibit optional as types inside lists/dicts to ensure forward ref checking works
    """
    if is_custom_field(field):
        conv = Any
    else:
        conv = FIELD_CONVERTERS[type(field)]

    # TODO: Is there a cleaner way to check for annotation types?
    if isinstance(conv, type) or conv.__module__ == "typing":
        pyd_type = conv
    else:
        pyd_type = conv(field)

    if not field.required and not no_optional:
        pyd_type = Optional[pyd_type]
    return pyd_type


def is_valid_field_name(bases, fld_name):
    try:
        # In Pydantic V2, we don't need to validate field names explicitly
        # This function now just checks if the field name is a valid Python identifier
        fld_name.isidentifier()
        return True
    except ValueError:
        return False


def get_alias(name):
    if name.endswith(ALIAS_MARKER):
        return name.replace(ALIAS_MARKER, "")
    return name


class MarshmallowModel(BaseModel):
    _schema = None

    @classmethod
    @root_validator(pre=True)
    def _schema_validate(cls, values):
        if not cls._schema:
            raise AssertionError("Must define a marshmallow schema")
        return cls._schema().load(values)  # pylint: disable=not-callable

    model_config = ConfigDict(
        alias_generator=get_alias
    )

def pydantic_from_marshmallow(src_schema, name=None):
    """Convert a marshmallow schema to a pydantic model. May only
    work for fairly simple cases. Barely tested. Enjoy."""

    if inspect.isclass(src_schema):
        if name is None:
            name = src_schema.__name__
            if name.endswith('Schema'):
                name = name[:-6]
        if callable(getattr(src_schema, 'schema', None)):
            src_schema = src_schema.schema()
    if name is None:
        if isinstance(src_schema, Schema):
            name = src_schema.__class__.__name__
        else:
            name = src_schema.__name__
        if name.endswith('Schema'):
            name = name[:-6]

    if name in pymm_cache:
        return pymm_cache[name]

    pymm_cache[name] = ForwardRef(name)

    pyd_fields = {}
    for field_name, field in src_schema._declared_fields.items():  # pylint: disable=protected-access
        pyd_type = get_pydantic_type(field)
        default = field.default if field.default != missing else None
        if field.data_key:
            field_name = field.data_key
        if not is_valid_field_name([BaseModel], field_name):
            field_name = field_name + ALIAS_MARKER
        
        # Use Field instead of directly creating a tuple
        pyd_fields[field_name] = (pyd_type, Field(default=default))

    # Automatically resolves forward refs
    pydantic_model = create_model(name, **pyd_fields, __base__=MarshmallowModel)
    pymm_cache[name] = pydantic_model
    return pydantic_model


# if __name__ == "__main__":
#     # Simple test...
#     def is_valid_str(val):
#         if not isinstance(val, str):
#             raise ValidationError(f"value is not a string: {val}")
#         return val

#     class MyField(fields.Field):
#         pass

#     class TestSchema(Schema):
#         some_str = fields.String(required=True, validate=is_valid_str)
#         some_dict = fields.Dict(keys=fields.Str(), default=None, missing={})
#         some_list = fields.List(fields.Integer)
#         fields = fields.Str()  # illegal field name for pydantic

#     class TestSubSchema(TestSchema):
#         some_int = fields.Integer(required=False, missing=5)
#         some_custom_field = MyField()

#     for schema in [TestSchema, TestSubSchema]:
#         model = pydantic_from_marshmallow(schema)
#         x = model(some_str="a string!")
#         print(f"\n{model}:{x}")
#         pprint(model.schema())