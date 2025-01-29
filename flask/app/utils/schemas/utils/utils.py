from marshmallow import (
    post_dump,
    pre_load,
    post_dump,
    post_load,
    pre_dump,
    ValidationError,
)
from datetime import datetime
from flask import Blueprint, jsonify

from app import ma
from app.utils.app.units import (
    Unit,
    convert_to_appropriate_unit,
    get_quantity_string,
    add_measurements,
    get_canonical_unit,
)
from app.utils.schemas.utils import UTCDateTime, ArgList

from .enums import EnumField
from .numbers import DecimalField
from flask_babel import lazy_gettext as _
from app.utils.schemas.utils.marshmallow_jsonschema.extensions import (
    SubmitReactJsonSchemaFormJSONSchema,
    DumpReactJsonSchemaFormJSONSchema
)

def injectSchema(*schemas):
    class InjectedSchema(*schemas):
        pass

    return InjectedSchema

class CreateUnitlessRequestSchema(ma.Schema):
    number_of_units = ma.Integer(
        required=False,
        load_only=True,
        load_default=1,
        metadata={"title": _("Number of Units"), "description": _("Number of instances to add")},
    )

    quantity_per_unit = ma.Integer(
        required=True,
        metadata={"title": _("Quantity Per Unit"), "description": _("Quantity of the new item per instance")},
        error_messages={"required": _("Item quantity is required")},
    )

    location_description = ma.String(
        required=False,
        load_default=None,
        metadata={"title": _("Location Description"), "description": _("Location where the item is stored")},
    )

    @pre_load
    def process_items(self, data, **kwargs):
        if "_type" in data and data["_type"] in data:
            data = {**data, **data.pop(data["_type"])}
        return data


class CreateRequestSchema(CreateUnitlessRequestSchema):
    unit = EnumField(
        enum=Unit,
        load_default=Unit.UNIT,
        metadata={"title":_("unit"), "description": _("The unit with which this item will be counted")},
    )


class QuantifiedSchema(ma.Schema):
    quantity = ma.Method("get_quantity", dump_only=True)

    locations = ma.List(ma.String, dump_only=True)

    rooms = ma.Pluck("RoomSchema", "name", many=True, dump_only=True)

    def get_quantity(self, obj):
        return get_quantity_string(
            obj.total_quantity, get_canonical_unit(obj.default_unit)
        )


class TooltipSchema(ma.Schema):
    class Meta:
        ordered = True

    value = ma.List(ma.String, dump_only=True)
    tooltip = ma.String(dump_only=True)


class PageSchema(ma.Schema):
    class Meta:
        ordered = True

    title = ma.String(dump_only=True)


class ActionSchema(ma.Schema):
    class Meta:
        ordered = True

    message = ma.String(required=False, metadata={"title":_("message"), "description": _("Message")})


class CardPlotSchema(ma.Schema):
    class Meta:
        ordered = True

    value = ma.String(dump_only=True)


class RequestSchemaMixin(ma.Schema):
    # created_at = UTCDateTime(
    #     required=False,
    #     allow_none=True,
    #     metadata={"title":_(""), "description": _("The date and time when the action was performed")},
    # )

    observation = ma.String(
        required=False,
        metadata={"title":_("observation"), "description": _("The observation associated with the given action")},
    )


class QueryTagsMixin(ma.Schema):
    tags = ArgList(
        ma.Integer(),
        required=False,
        load_default=None,
        load_only=True,
        metadata={"title":_("tags"), "description": _("filter by tags")},
    )



class SuggestionSchema(ma.Schema):
    class Meta:
        description = _("This schema represents Suggestions Model")

    id = ma.Integer(
        dump_only=True, data_key="id", metadata={"title":_("id"), "description": _("Unique Id of Plant")}
    )

    suggestion = ma.Method(
        "format_suggestion",
        dump_only=True,
        metadata={"title":_("suggestion"), "description": _("Suggestion of the entity")},
    )

    def format_suggestion(self, entity):
        if hasattr(entity, "suggestion"):
            return entity.suggestion
        elif hasattr(entity, "title"):
            return entity.title
        else:
            return f"#{entity.id}"


class TreeSuggestionSchema(ma.Schema):
    class Meta:
        description = _("This schema represents Suggestions of Tree Model")

    title = ma.String(
        dump_only=True, data_key="title", metadata={"title":_("title"), "description": _("Name of Tree")}
    )

    key = ma.String(
        dump_only=True, data_key="key", metadata={"title":_("key"), "description": _("Key of Tree")}
    )

    value = ma.String(
        dump_only=True, data_key="value", metadata={"title":_("value"), "description": _("Value of Tree")}
    )

    children = ma.List(
        ma.Nested("TreeSuggestionSchema"),
        dump_only=True,
        data_key="children",
    )





def get_bulk_schema(schema_class):
    class BulkSchema(schema_class):
        ids = ma.List(
            ma.Integer, required=True, metadata={"title":_("ids"), "description": _("List of ids")}
        )

    return BulkSchema


def get_chart_schema(schema_class):
    class ChartSchema(ma.Schema):
        class Meta:
            ordered = True

        result = ma.Nested(schema_class)

    return ChartSchema


def get_main_page_schema(schema_class):
    class MainPageSchema(schema_class, PageSchema):
        pass

    return MainPageSchema


def get_file_schema(schema_class):
    pass


def post_process_quantity(data, quantity_key="quantity", unit_key="unit", **kwargs):
    """
    This function is used to convert the quantity and unit to the appropriate unit.
    To create a pretty quantity string, use the FormattedQuantityField instead
    """
    if quantity_key not in data or unit_key not in data:
        return data

    quantity, unit = convert_to_appropriate_unit(
        data.get(quantity_key), data.get(unit_key), **kwargs
    )

    data[quantity_key] = quantity
    data[unit_key] = unit

    return data


def join_multiple_query_schemas(*schemas, exclude=None):
    class JoinedQuerySchema(ma.Schema):
        class Meta:
            ordered = True

        @post_load
        def split_data(self, data, **kwargs):
            models = set()
            for schema in schemas:
                models.add(schema.Meta.model.__name__.lower())

            def camel_to_snake(name):
                import re

                name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
                return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

            new_data = {}

            for key, value in data.items():
                for model_key in models:
                    if model_key in models:
                        if key.split(f"_")[0] == model_key:
                            var = camel_to_snake("_".join(key.split(f"_")[1:]))

                            try:
                                new_data[f"{model_key}_kwargs"].append(
                                    (
                                        var,
                                        value,
                                    )
                                )
                            except KeyError:
                                new_data[f"{model_key}_kwargs"] = [
                                    (
                                        var,
                                        value,
                                    )
                                ]

                            break

            return new_data

    exclude = exclude or []
    for schema in schemas:
        for field_name, field_obj in schema._declared_fields.items():
            if field_name not in exclude:
                new_field_name = f"{schema.Meta.model.__name__.lower()}_{field_name}"
                JoinedQuerySchema._declared_fields[new_field_name] = field_obj

    return JoinedQuerySchema


class InventoryQuantitySchema(ma.Schema):
    inventory_id = ma.Integer(
        required=True,
        load_only=True,
        metadata={"title":_("inventory_id"), "description": _("The instance we are taking this item from")},
        error_messages={"required": _("You must specify where you took the item from")},
    )

    quantity = DecimalField(
        required=True,
        metadata={"title":_("quantity"), "description": _("The quantity of item used")},
        error_messages={"required": _("You must specify the quantity used")},
    )

    unit = EnumField(enum=Unit, required=True)




# schemas for response .. [create new Item in the data base, update Item in the data base by id] routes
def get_response_schema(class_schema):
    class ResponseSchema(ma.Schema):
        class Meta:
            ordered = True

        success = ma.Boolean(dump_default=True, dump_only=True)
        result = ma.Nested(class_schema, many=False, dump_only=True)

    return ResponseSchema




def create_schema_blueprint(app):
    schema_bp = Blueprint("schema", __name__)

    return schema_bp



def extract_metadata_from_view(func):
    # Unwrap the function to get to the original
    if hasattr(func, "__wrapped__"):
            func = func.__wrapped__

    # Check if the function has a `_spec` attribute
    if hasattr(func, "_spec"):

        spec = getattr(func, "_spec", None)

        # Extract the body schema from the _spec attribute
        body_schema = spec.get("body", None)



        response_schema = None
        # trueodysseys-api  | Exception:  query_schema: None body_schema: (<KioskSchema(many=False)>, 'json')
        # extract the schema from the body_schema tuple
        if body_schema:
            if type(body_schema) == tuple:
                body_schema = body_schema[0]
        # You may also want to extract query schema (arguments schema)

        query_schema = spec.get("args", None)
        if query_schema:
            query_schema = query_schema[0]
            if type(query_schema) == tuple:
                query_schema = query_schema[0]

            # get response schema
            response_schema = spec.get("response", None)
            # get meta class of the response schema

            if response_schema:
                if type(response_schema) == tuple:
                    response_schema = response_schema[0]

                # get the meta class of the response schema
                if hasattr(response_schema, "Meta"):
                    if hasattr(response_schema.Meta, "orig_schema"):
                        response_schema = response_schema.Meta.orig_schema()

        return body_schema, query_schema, response_schema

    # Fallback if no _spec attribute is found
    return None, None, None


def generate_uischema(fields, elements_per_row, current_uischema):
    uischema = current_uischema or {}
    row_count = 1
    element_count = 0

    for field in fields:

        if uischema.get(field, {}).get("ui:widget") == "hidden":
            continue

        if element_count >= elements_per_row:
            row_count += 1
            element_count = 0
        

        try:
            uischema[field] |= {"row": str(row_count)}
        except KeyError:
            uischema[field] = {"row": str(row_count)}

        element_count += 1

    return uischema

def marshmallow_fields_to_antd_columns(schema, only=None, load_only=False, prefix=''):
    """
    Transforms marshmallow schema fields into a format suitable for antd tables.
    - schema: the marshmallow schema to transform.
    - only: a list of fields to include. If None, include all except load_only fields.
    - load_only: whether to include load_only fields.
    - prefix: used internally for nested fields.
    """
    # raise Exception(schema.fields)

    # check load only on the quantity field

    # Step 1: Filter fields to include
    fields_to_include = {
        name: field for name, field in schema.fields.items() if not field.load_only or load_only
    }


    # Step 2: Handle exclusion of specific fields
    _exclude = ("files", "comments")

    # Remove from _exclude those fields that are not in fields_to_include
    _exclude = [field for field in _exclude if field in fields_to_include]

    # Add schema-level excludes to the _exclude list
    if schema.exclude:
        _exclude = list(set(_exclude) | set(schema.exclude))

    # Remove excluded fields from fields_to_include
    fields_to_include = {
        name: field for name, field in fields_to_include.items() if name not in _exclude
    }

    # Step 3: Handle react_uischema_extra and UI order
    meta_exists = hasattr(schema, 'Meta')
    react_uischema_extra = getattr(schema.Meta, "react_uischema_extra", {}) if meta_exists else {}

    all_field_names = list(fields_to_include.keys())

    uischema = {}  # This will store UI schema details, including column order

    # Add react_uischema_extra entries to uischema
    for k, v in react_uischema_extra.items():
        uischema[k] = v

    if 'ui:order' in react_uischema_extra:
        ui_order = react_uischema_extra['ui:order']
        # Append any fields not already in 'ui:order'
        remaining_fields = [f for f in all_field_names if f not in ui_order]
        react_uischema_extra['ui:order'].extend(remaining_fields)
    else:
        ui_order = all_field_names  # Use natural order if no UI order is specified

    antd_table_extra = getattr(schema.Meta, "antd_table_extra", {}) if meta_exists else {}

    # Step 4: Process the fields, considering the "only" parameter and nested fields
    antd_columns = []
    for field_name in ui_order:
        if field_name not in fields_to_include:
            continue

        field_obj = fields_to_include[field_name]

        # Skip fields not in the 'only' list, if 'only' is specified
        if only and field_name not in only:
            continue

        # Handle nested fields (nested schema)
        if isinstance(field_obj, ma.Nested):
            # nested_schema = field_obj.schema
            # nested_columns = marshmallow_fields_to_antd_columns(
            #     nested_schema,
            #     only=field_obj.only if field_obj.only else None,
            #     load_only=load_only,
            #     prefix=f"{prefix}{field_name}."
            # )
            # antd_columns.extend(nested_columns)
            continue
        else:
            # Create a column for the antd table

            title = field_obj.metadata.get('title', f"{prefix}{field_name}")

            # Create a column for the antd table
            column = {
                "title": title,  # Use metadata title if it exists
                "dataIndex": f"{prefix}{field_name}",
                "key": f"{prefix}{field_name}",
                "width": max(title.__len__() * 11, 90)
            }
            if field_name in antd_table_extra:
                extra = antd_table_extra[field_name]
                if 'component' in extra:
                    # Assume the 'component' is some React component that needs to be rendered
                    column['render'] = extra['component']  # You'll need to replace this with appropriate render logic in your frontend


            antd_columns.append(column)

        # Step 6: Reorder columns to place id first, and inserted_at and updated_at last
        id_column = next((col for col in antd_columns if col['key'] == 'id'), None)
        inserted_at_column = next((col for col in antd_columns if col['key'] == 'inserted_at'), None)
        updated_at_column = next((col for col in antd_columns if col['key'] == 'updated_at'), None)

        # Remove these columns if they exist so we can reinsert them in the correct order
        antd_columns = [col for col in antd_columns if col['key'] not in ['id', 'inserted_at', 'updated_at']]

        # Insert id column at the start
        if id_column:
            antd_columns.insert(0, id_column)

        # Append inserted_at and updated_at columns at the end
        if inserted_at_column:
            antd_columns.append(inserted_at_column)
        if updated_at_column:
            antd_columns.append(updated_at_column)


    return antd_columns



def update_blueprints_with_schemas(app, target_bp, ignore_methods=["OPTIONS", "HEAD"]):
    for bp in app.blueprints.values():
        for rule in app.url_map.iter_rules():
            if rule.endpoint.startswith(bp.name + "."):
                

                authed_route = False
                methods = list(rule.methods - {"OPTIONS", "HEAD"})

                endpoint_func = app.view_functions[rule.endpoint]
                
                from app.utils.app import get_canonical_route
                route_path = get_canonical_route(rule.rule)
                if route_path.split("/")[0] not in ["api"]:
                    continue
                for method in set(rule.methods) - set(ignore_methods):
                    
                    if hasattr(endpoint_func, "_spec"):
                        if endpoint_func._spec.get("auth", False):
                            authed_route = True
                            break

                # get the body schema from the view function
                body_schema, query_schema, response_schema = extract_metadata_from_view(
                    endpoint_func
                )
                if body_schema or query_schema or response_schema:
                    schema_route = f"{rule.rule}/schema"

                    # Define the schema route dynamically
                    def create_schema_view(
                        schema, query_schema, response_schema, schema_route, methods
                    ):
                        

                        def schema_view(*args, **kwargs):

                            # Handle the dynamic route parameters passed in *args and **kwargs

                            response = {}
                            if schema:
                                (
                                    response["schema"],
                                    response["ui_schema"],
                                ) = SubmitReactJsonSchemaFormJSONSchema().dump_with_uischema(
                                    schema
                                )

                            if query_schema:

                                (
                                    response["query_schema"],
                                    response["query_ui_schema"],
                                ) = SubmitReactJsonSchemaFormJSONSchema().dump_with_uischema(
                                    query_schema
                                )

                            if response_schema:
                                # raise Exception(response_schema._declared_fields)
                                # (
                                #     response["response_schema"],
                                #     response["response_ui_schema"],
                                # ) = DumpReactJsonSchemaFormJSONSchema().dump_with_uischema(
                                #     response_schema
                                # )
                                response["response_schema"] = marshmallow_fields_to_antd_columns(response_schema)


                            return jsonify(response)

                        # Generate a unique name for the schema view function based on route and methods
                        methods_str = "_".join(
                            sorted(method.lower() for method in methods)
                        )  # Join methods as part of the name
                        route_str = schema_route.replace("/", "_").strip(
                            "_"
                        )  # Clean and normalize route
                        schema_view.__name__ = f"schema_view_{route_str}_{methods_str}"
                        if authed_route:
                            from app.api.auth import token_auth
                            from apifairy import authenticate
                            schema_view = authenticate(token_auth)(schema_view)

                        return schema_view

                    # Register the dynamically created schema route directly in the blueprint
                    unique_function = create_schema_view(
                        schema=body_schema,
                        query_schema=query_schema,
                        schema_route=schema_route,
                        response_schema=response_schema,
                        methods=methods,
                    )
                    target_bp.route(schema_route, methods=methods)(unique_function)


class GenericLoadDumpField(ma.Field):
    def __init__(self, load_schema, dump_schema, many=False, **kwargs):
        self.load_schema_class = load_schema
        self.dump_schema_class = dump_schema
        self.many = many  # Store the many parameter
        
        super().__init__(**kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        # Instantiate the schema with the 'many' argument
        schema = self.load_schema_class(many=self.many)
        return schema.load(value)

    def _serialize(self, value, attr, obj, **kwargs):
        # Instantiate the schema with the 'many' argument
        schema = self.dump_schema_class(many=self.many)
        return schema.dump(value)