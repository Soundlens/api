from ..base import JSONSchema
from app import ma



class ReactJsonSchemaFormJSONSchema(JSONSchema):
    """
    Usage (assuming marshmallow v3):

    class MySchema(Schema):
        first_name = fields.String(
            metadata={
                'ui:autofocus': True,
            }
        )
        last_name = fields.String()

        class Meta:
            react_uischema_extra = {
                'ui:order': [
                    'first_name',
                    'last_name',
                ]
            }

    json_schema_obj = ReactJsonSchemaFormJSONSchema()
    json_schema, uischema = json_schema_obj.dump_with_uischema(MySchema())
    """

    def dump_with_uischema(self, obj, many=None, *args):
        """Runs both dump and dump_uischema"""

        # Check if obj is a OneOfSchema
        if hasattr(obj, 'type_schemas'):
            dump = self._dump_oneof_schema(obj, many=many, *args)
        else:
            dump = self.dump(obj, *args, many=many)

        uischema = self.dump_uischema(obj, *args, many=many)
        return dump, uischema
    
    def dump_uischema(self, obj, many=None, *args):
        """
        Generate a uiSchema for react-jsonschema-form that hides '_type' fields recursively
        in nested schemas and list items, properly addressing each nested structure within the main schema.
        """

        def recursive_hide_type(schema, path=[]):
            """
            Recursively hide 'type_field' fields, adapting uiSchema based on schema structure.
            Updates the uischema dictionary in place.
            """
            # Hide type_field for the current schema level if not at the root
            if path:
                type_path = path + [getattr(schema, 'type_field', '_type')]
                dict_set_nested(uischema, type_path, {'ui:widget': 'hidden'})
                type_schemas = getattr(schema, 'type_schemas', None)
                if type_schemas:
                    for key, type_schema in type_schemas.items():
                        recursive_hide_type(type_schema, path)

            # Determine the fields of the schema, considering different ways fields can be stored
            fields = getattr(schema, 'fields', {}).items() or getattr(schema, '_declared_fields', {}).items()
            from ...utils import GenericLoadDumpField

            for field_name, field in fields:
                current_path = path + [field_name]
                # Check if the field is a list containing nested schemas
                if isinstance(field, ma.List) and isinstance(field.inner, ma.Nested):
                    # Handle the nested schema for list items
                    nested_schema_path = current_path + ['items']
                    recursive_hide_type(field.inner.nested, nested_schema_path)
                # Check if the field itself is a nested schema
                elif isinstance(field, ma.Nested):
                    recursive_hide_type(field.nested, current_path)

                elif isinstance(field, GenericLoadDumpField):
                    # how to know if it is a load or dump schema?
                    schema = field.load_schema_class()
                    recursive_hide_type(schema, current_path)


        def dict_set_nested(dic, keys, value):
            """
            Set a value in a nested dictionary based on a list of keys.
            """
            for key in keys[:-1]:
                dic = dic.setdefault(key, {})
            dic[keys[-1]] = value

        # Initialize the uiSchema, optionally starting with predefined settings
        uischema = {}
        if hasattr(self, '_dump_uischema_iter'):
            uischema.update(self._dump_uischema_iter(obj, *args, many=many))

        # Apply the recursive hiding function to the base object schema
        recursive_hide_type(obj)

        return uischema

    def _dump_uischema_iter(self, obj, many=None, *args):
        """
        Recursively builds the UI schema for ReactJsonSchemaFormJSONSchema.dump_uischema,
        applying react_uischema_extra for nested schemas, including lists of nested schemas,
        and ensuring no duplicate values. Handles cases where obj is a string by resolving
        it to the corresponding schema.
        """

        # Schema registry or resolver - Example, replace with actual schema resolution logic
        # schema_registry = {
        #     "UserSchema": UserSchema,  # Example mapping
        #     "ActivityItemsRelationSchema": ActivityItemsRelationSchema,
        #     # Add other schema mappings here
        # }

        # def resolve_schema(schema_reference):
        #     """Resolves a schema reference (string) to the actual schema object."""
        #     if isinstance(schema_reference, str):
        #         print(f"Resolving schema from string: {schema_reference}", flush=True)
        #         return schema_registry.get(schema_reference)
        #     return schema_reference

        def build_uischema(obj):
            uischema = {}

            # Resolve the schema if obj is a string
            # obj = resolve_schema(obj)

            if isinstance(obj, str):
                return uischema
            # if obj is None:
            #     raise ValueError("Unable to resolve schema from reference.")

            # Check if Meta exists and has the react_uischema_extra attribute
            meta_exists = hasattr(obj, 'Meta')
            react_uischema_extra = getattr(obj.Meta, "react_uischema_extra", {}) if meta_exists else {}

            all_field_names = list(obj._declared_fields.keys())

            # Add react_uischema_extra entries to uischema
            for k, v in react_uischema_extra.items():
                # print(f"Adding from react_uischema_extra -> Key: {k}, Value: {v}", flush=True)
                uischema[k] = v

            if 'ui:order' in react_uischema_extra:
                ui_order = react_uischema_extra['ui:order']
                # Append any fields not already in 'ui:order'
                remaining_fields = [f for f in all_field_names if f not in ui_order]
                react_uischema_extra['ui:order'].extend(remaining_fields)

            # Process obj.fields and add metadata with "ui:" prefixes to uischema
            for field_name, field in obj._declared_fields.items():

                if field.dump_only:
                    continue
                
                metadata = field.metadata.get("metadata", {})
                metadata.update(field.metadata)

                filtered_metadata = {k: v for k, v in metadata.items() if k.startswith("ui:")}
                if filtered_metadata:
                    # Add metadata to the uischema
                    # print(f"Adding from fields -> Field Name: {field_name}, Metadata: {filtered_metadata}", flush=True)
                    uischema[field_name] = uischema.get(field_name, {})
                    uischema[field_name].update(filtered_metadata)

                # Check if the field is a list of nested schemas (e.g., ma.List(ma.Nested(...)))
                if isinstance(field, ma.List) and isinstance(field.inner, ma.Nested):
                    # print(f"Processing list of nested schemas for field: {field_name}", flush=True)
                    nested_schema = field.inner.nested
                    # Recursively build the nested schema for the list items
                    nested_uischema = build_uischema(nested_schema)

                    # Add the nested schema under the field_name
                    uischema[field_name] = {"items": nested_uischema}

                # Check if the field itself contains nested schemas (for recursive handling)
                elif isinstance(field, ma.Nested):
                    # print(f"Processing nested schema for field: {field_name}", flush=True)
                    # Recursively build the nested schema
                    nested_uischema = build_uischema(field.nested)

                    # Merge the nested schema into the current field's uischema
                    uischema[field_name] = uischema.get(field_name, {})
                    uischema[field_name].update(nested_uischema)

            return uischema

        # Start the recursive building of uischema from the root schema object
        return build_uischema(obj)

class SubmitReactJsonSchemaFormJSONSchema(ReactJsonSchemaFormJSONSchema):
    def dump(self, schema, many=None, exclude=(), only=(), partial=None, unknown=None):
        # Copy the original fields dictionary
        
        print(f"schema: {schema.fields}", flush=True)
        fields_to_include = {
            name: field for name, field in schema.fields.items() if not field.dump_only
        }

        # Create a new schema with only the filtered fields
        filtered_schema = schema.__class__(only=fields_to_include.keys())

        # Generate the JSON schema with the filtered fields
        return super().dump(filtered_schema)


class DumpReactJsonSchemaFormJSONSchema(ReactJsonSchemaFormJSONSchema):
    def dump(self, schema, many=None, exclude=(), only=(), partial=None, unknown=None):
        # Copy the original fields dictionary

        # ignore the load_only fields
        fields_to_include = {
            name: field for name, field in schema.fields.items() if not field.load_only
        }
        
        _exclude = (
            "files",
            "comments",
        )
        # check if the fields are in the class_kwargs
        for field in _exclude:
            if field not in fields_to_include.keys():
                # remove the field from the exclude list
                _exclude = [x for x in _exclude if x != field]

        if schema.exclude:
            _exclude = _exclude + list(schema.exclude)

        # Create a new schema with only the filtered fields
        filtered_schema = schema.__class__(only=fields_to_include.keys(), exclude=tuple(_exclude))

        # Generate the JSON schema with the filtered fields
        return super().dump(filtered_schema)