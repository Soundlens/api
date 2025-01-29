from functools import wraps

from app.exceptions import BusinessLogicException


def suppress_exception(f):
    """
    Usage:
    @suppress_exception
    def foo():
        pass

    Decorator that suppresses BusinessLogicException.
    It consumes an additional argument `_raise` that defaults to True.
    If the decorated function raises a BusinessLogicException and _raises is True,
        the exception is raised.
    If the decorated function raises a BusinessLogicException and _raises is False,
        the exception is suppressed and None is returned
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        _raise = kwargs.pop("_raise", True)
        try:
            return f(*args, **kwargs)
        except BusinessLogicException as e:
            if _raise:
                raise e
            return None

    return wrapper


def convert_to_list(*keys):
    """
    This function receives a list of keywords and returns a decorator
    that assures that all the kwargs passed to a function that are in
    the given `keys` argument will be a list.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            for k, v in kwargs.items():
                if k in keys and v is not None and type(v) is not list:
                    kwargs[k] = [v]
            return f(*args, **kwargs)

        return wrapper

    return decorator


def get_user_arg(f):
    """
    This decorator assures that the decorated function will receive a user
    If no user is specified, the function receives the logged user
    """
    from app.utils.app import get_logged_user

    @wraps(f)
    def wrapper(*args, user: "User" = None, **kwargs):
        if user is None:
            user = get_logged_user()
        return f(*args, user=user, **kwargs)

    return wrapper


def create_join_once():
    """
    This is a function factory that returns a function that helps assuring
    that a query joins a table only once, even if it is called multiple times.
    We need it to be a function factory because we want the joined_entities
    to be scoped to the function that calls it, not to the whole module.

    Usage:
    def search(**kwargs):
        join_once = create_join_once()

        query = db.session.query(Entity)

        if some_expression:
            query = join_once(query, Table, join_condition, other_arguments)
            ...

        if some_other_expression:
            query = join_once(query, Table, join_condition, other_arguments)
            ...

    Even if both expressions are True, the query will only join the table once!!
    NOTE: This function only considers the table name, not the join condition!
    TODO: consider all the arguments passed to the join function
    """

    joined_entities = set()

    def join_once(query: "Query", table: "Table", *args, **kwargs) -> "Query":
        nonlocal joined_entities
        join_key = table
        if join_key not in joined_entities:
            joined_entities.add(join_key)
            query = query.join(table, *args, **kwargs)
        return query

    return join_once
