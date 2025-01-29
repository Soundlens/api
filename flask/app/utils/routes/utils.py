from app.utils.app.file import reader_from_b64
from app.utils.services import NewFileData, NewTagData
from app.utils.app.file import IMAGE_FORMATS
from app.api.exceptions import BusinessLogicException


def create_enum_route(
    bp, route_name, enum_class, auth_required=True, additional_responses=None
):

    from apifairy import authenticate, body, response, other_responses, arguments
    from flask import jsonify

    """
    Helper function to create a route for an enum suggestion.
    
    :param bp: The Blueprint object
    :param route_name: The route name (e.g., 'activity_types')
    :param enum_class: The Enum class (e.g., ActivityType)
    :param auth_required: Whether authentication is required (default: True)
    :param additional_responses: Any additional responses (default: None)
    """

    # Define the route function with a unique name
    def route_function():
        return jsonify(enum_class.suggestion())

    # Create the URL path
    url_path = f"/enums/{route_name}"

    # Generate a unique endpoint name
    endpoint_name = f"get_enum_{route_name}"

    # Define the route decorator
    decorators = []
    if auth_required:
        from app.api.auth import token_auth, check_permission

        decorators.append(authenticate(token_auth))
    if additional_responses:
        decorators.append(other_responses(additional_responses))

    # Apply the decorators to the route function
    for decorator in decorators:
        route_function = decorator(route_function)

    # Add the route function to the blueprint
    # print(f"Adding route: {url_path}")
    bp.add_url_rule(url_path, view_func=route_function, endpoint=endpoint_name)


def get_file_data(files):
    result = []
    for f in files:
        result.append(NewFileData(f["name"], reader_from_b64(f["base64"])))
    return result


def get_tags_data(tags):
    result = []
    for f in tags:
        result.append(NewTagData(f))
    return result


def get_image_data(upload_files):
    new_files = []
    for file in upload_files:
        if file["type"] in IMAGE_FORMATS:
            new_files.append(NewFileData(file["name"], reader_from_b64(file["base64"])))
        else:
            raise BusinessLogicException(
                description=f"File {file['name']} is not a image",
                code=400,
            )
    return new_files


def fake_pagination(items, total, page, per_page):
    return {
        "result": items,
        "pagination": {
            "has_next": total > page * per_page,
            "count": total,
            "page": page,
            "per_page": per_page,
        },
    }


def format_suggestion(id: str, suggestion: str = None):
    if suggestion is None:
        suggestion = id
    return {"id": id, "suggestion": suggestion}


def format_response_message(data):
    return {"message": data}


def format_response_schema(data):
    return {"success": True, "result": data}

def dynamic_body(schema_cls):
    from functools import wraps
    from marshmallow import ValidationError
    from flask import request
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Reinitialize the schema with all dynamic fields
            # check if schema_cls is a class or an instance
            if isinstance(schema_cls, type):
                schema = schema_cls()
            else:
                schema = schema_cls

            # Validate and deserialize the request body
            try:
                json_data = request.get_json()
                validated_data = schema.load(json_data)
            except ValidationError as err:
                return {"errors": err.messages}, 400

            # Merge the validated data with existing kwargs
            kwargs['data'] = validated_data
            # Call the original function with the validated args
            return func(*args, **kwargs)

        # Update the function's _spec attribute (or the appropriate attribute)
        if not hasattr(func, '_spec'):
            func._spec = {}
        
        func._spec['body'] = schema_cls() if isinstance(schema_cls, type) else schema_cls
        
        return wrapper

    return decorator


def get_all_suggestions_entities(bp, service, query_schema, description, entity_name):
    """Registers a route and dynamically generates the function"""
    from app.utils.schemas.utils import SuggestionSchema, TreeSuggestionSchema

    suggestion_schema = SuggestionSchema(many=True)
    tree_suggestion_schema = TreeSuggestionSchema(many=True)
    from apifairy import authenticate, response, other_responses, arguments

    @bp.route(f"/suggestions/{entity_name}", methods=["GET"])
    @arguments(
        query_schema(
            exclude=(
                "page",
                "per_page",
            )
        )
    )
    @response(suggestion_schema, 200, description=description)
    @other_responses({404: f"{entity_name} not found"})
    def handler(args):
        page = args.pop("page", 1)
        per_page = args.pop("per_page", 10)
        entities = service.search(**args)
        return entities.all()

    # Assigning a unique name to the function
    handler.__name__ = f"get_all_{entity_name}"
    return handler
