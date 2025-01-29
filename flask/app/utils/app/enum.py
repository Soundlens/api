import os
from enum import StrEnum
from typing import List
from sqlalchemy import select, union, literal


class Enum(StrEnum):
    @classmethod
    def all_values(cls):
        return [e.value for e in cls]

    @classmethod
    def exclude(cls, exclude_fields) -> "Enum":
        return Enum(
            f'{cls.__name__}_without_{"_".join([f.value for f in exclude_fields])}', {
                v.name: v.value for v in cls if v not in exclude_fields},
        )

    @classmethod
    def from_string(cls, value):
        for member in cls.__members__.values():
            if member.value == value:
                return member

        raise ValueError(f"{value} is not a valid value for {cls.__name__}")

    @classmethod
    def fake_table(cls, label="value"):
        from app.main import db

        return db.session.query(
            union(*[select(literal(x).label(label)) for x in cls.all_values()]).alias(
                "enum_values"
            )
            # .label(label)
        )

    @classmethod
    def only(cls, fields: List["Enum"]) -> "Enum":
        return Enum(
            f'{cls.__name__}_only_{"_".join([f.value for f in fields])}',
            {v.name: v.value for v in cls if v in fields},
        )

    # @classmethod
    # def from_enum_list(cls, values: List["Enum"]):
    #     combined_enum = {}
    #     for enum in values:
    #         combined_enum.update(enum.__members__)

    #     return Enum(cls.__name__, combined_enum)

    # CombinedEnum = Enum.from_enum_list(Enum1, Enum2)

    @classmethod
    def from_set(cls, values) -> "Enum":
        return Enum(cls.__name__, {v: v for v in values})

    @classmethod
    def suggestion(cls, only=None):
        if only is not None:
            fields = only
        else:
            fields = [e for e in cls]

        return [{"id": e.value, "suggestion": e} for e in fields]

    @classmethod
    def get_enum(cls, enum=True):
        from app.main import db

        if enum:
            return db.Enum(
                cls,
                values_callable=lambda cls: cls.all_values(),
                name=f"{cls.__name__}_enum",
                native_enum=False,
            )
        else:
            return db.String(max([len(v) for v in cls.all_values()]))

    # @classmethod
    # def get_enum(cls, enum=False):
    #     from app.main import db

    #     if enum:
    #         return db.Enum(
    #             cls,
    #             values_callable=lambda cls: cls.all_values(),
    #             name=f"{cls.__name__}_enum",
    #             native_enum=False,
    #         )
    #     else:
    #         return db.String(255)

    def __repr__(self):
        return self.value
