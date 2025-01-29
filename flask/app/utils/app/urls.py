import os
import re


def get_canonical_route(route: str) -> str:
    res = re.sub(r"<.*?>", "", route)
    if res[0] == "/":
        res = res[1:]
    return res


def get_base_url() -> str:

    env = os.environ.get("APP_ENV")

    if env == "prod":
        return f"https://{os.environ.get('WEB_APP_HOST', 'localhost')}"

    return f"http://{os.environ.get('WEB_APP_HOST', 'localhost')}:{os.environ.get('WEB_APP_PORT', '3000')}"


def get_email_verification_url(token: str) -> str:
    return f"{get_base_url()}/verify_email?token={token}"


def get_complete_registration_url(token: str) -> str:
    return f"{get_base_url()}/complete_registration?token={token}"


def get_recover_password_url(token: str) -> str:
    return f"{get_base_url()}/recover_password?token={token}"


def get_app_routes(app, ignore_methods=["OPTIONS", "HEAD"], decorated_only=True):
    """
    Returns all the application routes. The result is a list of tuples:
    [ (route_path: str, method: str, action: str), ...]
    """
    from app.api.auth import associate_action

    result = []

    for rule in app.url_map.iter_rules():
        endpoint_func = app.view_functions[rule.endpoint]

        route_path = get_canonical_route(rule.rule)
        if route_path.split("/")[0] not in ["api"]:
            continue
        for method in set(rule.methods) - set(ignore_methods):
            action = None
            decorated = False
            if (
                getattr(endpoint_func, "decorated_function", None)
                == associate_action.__name__
            ):
                decorated = True
                action = endpoint_func.decorated_args

            if (decorated_only and decorated) or not decorated_only:
                result.append((route_path, method, action))
    return result


def get_backoffice_url_for_entity(entity, id):
    match entity:
        case "attendees":
            return get_base_url() + f"/attendee/{id}"
        case "events":
            return get_base_url() + f"/event/{id}"
