from marshmallow import ValidationError

from app import ma
from app.utils.app.units import get_unit_from_string


class EnumField(ma.Field):
    def __init__(self, enum, *args, **kwargs):
        self.enum = enum
        super().__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        if value not in self.enum.all_values():
            raise ValidationError(
                f"Invalid value for {self.enum.__name__}: {value}. Must be one of {self.enum.all_values()}"
            )
        return self.enum(value)

    def _jsonschema_type_mapping(self):
            return {
                'type': 'string',
                'enum': self.enum.all_values()
            }


    def __name__(self):
        return self.enum.__name__


class EnumList(ma.Field):
    """
    The enum_attr argument is the name of the attribute where the enum is stored.
    """

    def __init__(self, enum, enum_attr, *args, **kwargs):
        self.enum = enum
        self.enum_attr = enum_attr
        super().__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return [getattr(v, self.enum_attr) for v in value]

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        if type(value) is not list:
            raise ValidationError(f"{attr} must be a list")
        errors = [
            f"Invalid value for {self.enum.__name__}: {v}. Must be one of {self.enum.all_values()}"
            for v in value
            if v not in self.enum.all_values()
        ]
        if errors != []:
            raise ValidationError(errors)
        return [self.enum(v) for v in value]
