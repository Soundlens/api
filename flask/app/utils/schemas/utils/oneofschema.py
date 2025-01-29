from collections import defaultdict
from app import ma
from marshmallow import (
    ValidationError,
)
from werkzeug.datastructures import ImmutableMultiDict
from webargs.multidictproxy import MultiDictProxy
from flask_babel import lazy_gettext as _


class OneOfSchema(ma.Schema):
    """
    This is a special kind of schema that actually multiplexes other schemas
    based on object type. When serializing values, it uses get_obj_type() method
    to get object type name. Then it uses `type_schemas` name-to-Schema mapping
    to get schema for that particular object type, serializes object using that
    schema and adds an extra "type" field with name of object type.
    Deserialization is reverse.

    Example:

        class Foo(object):
            def __init__(self, foo):
                self.foo = foo

        class Bar(object):
            def __init__(self, bar):
                self.bar = bar

        class FooSchema(marshmallow.Schema):
            foo = marshmallow.fields.String(required=True)

            @marshmallow.post_load
            def make_foo(self, data, **kwargs):
                return Foo(**data)

        class BarSchema(marshmallow.Schema):
            bar = marshmallow.fields.Integer(required=True)

            @marshmallow.post_load
            def make_bar(self, data, **kwargs):
                return Bar(**data)

        class MyUberSchema(marshmallow.OneOfSchema):
            type_schemas = {
                'foo': FooSchema,
                'bar': BarSchema,
            }

            def get_obj_type(self, obj):
                if isinstance(obj, Foo):
                    return 'foo'
                elif isinstance(obj, Bar):
                    return 'bar'
                else:
                    raise Exception('Unknown object type: %s' % repr(obj))

        MyUberSchema().dump([Foo(foo='hello'), Bar(bar=123)], many=True)
        # => [{'type': 'foo', 'foo': 'hello'}, {'type': 'bar', 'bar': 123}]

    You can control type field name added to serialized object representation by
    setting `type_field` class property.
    """

    type_field = "type"
    type_field_remove = True
    type_field_dump = True
    type_schemas = {}
    exclude_schemas = ()

    def __init__(self, **kwargs):
        only = kwargs.get("only")
        exclude = kwargs.get("exclude", ())
        exclude_schemas = kwargs.pop("exclude_schemas", ())
        if only is not None:
            self.type_field_dump = self.type_field in only
            kwargs["only"] = ()
        if exclude:
            self.type_field_dump = self.type_field not in exclude
            kwargs["exclude"] = ()

        if exclude_schemas:
            self.type_schemas = {
                k: v
                for k, v in self.type_schemas.items()
                if k not
                  in exclude_schemas
            }

        # only, exclude = self._normalize_nested_options() # if we want to integrate the nested options ie. only = ('name', 'address.city') which will only dump the name and address.city
        super().__init__(**kwargs)

        self._init_type_schemas(only, exclude)

    # def _normalize_nested_options(self, only=None, exclude=None):
    #     """Apply then flatten nested schema options.
    #     This method is private API.
    #     """
    #     if only is not None:
    #         # Apply the only option to nested fields.
    #         self.__apply_nested_option("only", only, "intersection")
    #         # Remove the child field names from the only option.
    #         only = self.set_class([field.split(".", 1)[0] for field in self.only])
    #     if exclude:
    #         # Apply the exclude option to nested fields.
    #         self.__apply_nested_option("exclude", exclude, "union")
    #         # Remove the parent field names from the exclude option.
    #         exclude = self.set_class(
    #             [field for field in self.exclude if "." not in field]
    #         )

    #     return only, exclude

    # def __apply_nested_option(self, option_name, field_names, set_operation) -> None:
    #         """Apply nested options to nested fields"""
    #         # Split nested field names on the first dot.
    #         nested_fields = [name.split(".", 1) for name in field_names if "." in name]
    #         # Partition the nested field names by parent field.
    #         nested_options = defaultdict(list)  # type: defaultdict
    #         for parent, nested_names in nested_fields:
    #             nested_options[parent].append(nested_names)
    #         # Apply the nested field options.
    #         for key, options in iter(nested_options.items()):
    #             new_options = self.set_class(options)
    #             original_options = getattr(self.declared_fields[key], option_name, ())
    #             if original_options:
    #                 if set_operation == "union":
    #                     new_options |= self.set_class(original_options)
    #                 if set_operation == "intersection":
    #                     new_options &= self.set_class(original_options)
    #             setattr(self.declared_fields[key], option_name, new_options)

    def _init_type_schemas(self, only, exclude):
        self.type_schemas = {
            k: self._create_type_schema_instance(v, only, exclude)
            for k, v in self.type_schemas.items()
        }

    def _create_type_schema_instance(self, SchemaCls, only, exclude):
        if only or exclude:
            if SchemaCls.opts.fields:
                available_field_names = self.set_class(SchemaCls.opts.fields)
            else:
                available_field_names = self.set_class(
                    SchemaCls._declared_fields.keys()
                )

                if SchemaCls.opts.additional:
                    available_field_names |= self.set_class(SchemaCls.opts.additional)
            if only:
                only = self.set_class(only) & available_field_names
            if exclude:
                exclude = self.set_class(exclude) & available_field_names

        return SchemaCls(only=only, exclude=exclude)

    def get_obj_type(self, obj):
        """Returns name of the schema during dump() calls, given the object
        being dumped."""
        # return obj.__class__.__name__
        return getattr(obj, self.type_field)

    def get_data_type(self, data):
        """Returns name of the schema during load() calls, given the data being
        loaded. Defaults to looking up `type_field` in the data."""
        data_type = data.get(self.type_field)
        if self.type_field in data and self.type_field_remove:
            data.pop(self.type_field)
        return data_type

    def dump(self, obj, *, many=None, **kwargs):
        errors = {}
        result_data = []
        result_errors = {}
        many = self.many if many is None else bool(many)

        if not many:
            result = result_data = self._dump(obj, **kwargs)
        else:
            for idx, o in enumerate(obj):
                try:

                    result = self._dump(o, **kwargs)
                    result_data.append(result)
                except ValidationError as error:
                    result_errors[idx] = error.normalized_messages()
                    result_data.append(error.valid_data)

        result = result_data
        errors = result_errors

        if not errors:
            return result
        else:
            exc = ValidationError(errors, data=obj, valid_data=result)
            raise exc

    def _dump(self, obj, *, update_fields=True, **kwargs):
        obj_type = self.get_obj_type(obj)


        if obj_type is None:
            return (
                None,
                {"_schema": _("Unknown object class: %s") % obj.__class__.__name__},
            )
        schema = self.type_schemas.get(obj_type)

        if not schema:
            return None, {"_schema": _("Unsupported object type: %s") % obj_type}

        schema.context.update(getattr(self, "context", {}))

        result = schema.dump(obj, many=False, **kwargs)
        if result is not None and self.type_field_dump:

            # raise Exception(obj_type)
            result[self.type_field] = getattr(obj, self.type_field, obj_type)
        return result

    def load(self, data, *, many=None, partial=None, unknown=None, **kwargs):
        errors = {}
        result_data = []
        result_errors = {}
        many = self.many if many is None else bool(many)
        if partial is None:
            partial = self.partial
        if not many:
            try:
                result = result_data = self._load(
                    data, partial=partial, unknown=unknown, **kwargs
                )
                #  result_data.append(result)
            except ValidationError as error:
                result_errors = error.normalized_messages()
                result_data.append(error.valid_data)
        else:
            for idx, item in enumerate(data):
                try:
                    result = self._load(item, partial=partial, **kwargs)
                    result_data.append(result)
                except ValidationError as error:
                    result_errors[idx] = error.normalized_messages()
                    result_data.append(error.valid_data)

        result = result_data
        errors = result_errors

        if not errors:
            return result
        else:
            exc = ValidationError(errors, data=data, valid_data=result)
            raise exc

    def _load(self, data, *, partial=None, unknown=None, **kwargs):
        if not isinstance(data, dict) and not isinstance(data, MultiDictProxy):
            raise ValidationError({"_schema": "Invalid data type: %s" % data})

        data = dict(data)
        unknown = unknown or self.unknown
        data_type = self.get_data_type(data)

        if data_type is None:
            raise ValidationError(
                {self.type_field: [_("Missing data for required field.")]}
            )

        try:
            schema = self.type_schemas.get(data_type)
        except TypeError:
            # data_type could be unhashable
            raise ValidationError({self.type_field: [_("Invalid value: %s") % data_type]})
        if not schema:
            raise ValidationError(
                {self.type_field: [_("Unsupported value: %s") % data_type]}
            )

        schema.context.update(getattr(self, "context", {}))

        return schema.load(data, many=False, partial=partial, unknown=unknown, **kwargs)

    def validate(self, data, *, many=None, partial=None):
        try:
            self.load(data, many=many, partial=partial)
        except ValidationError as ve:
            return ve.messages
        return {}
