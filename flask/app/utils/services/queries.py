from functools import wraps
from datetime import datetime
from typing import Type, List
from sqlalchemy import func, case, union_all, literal, inspect
from sqlalchemy.sql import text

from app import db
from app.exceptions import BusinessLogicException, ImplementationException
from app.utils.app import convert_to_list, get_model_from_tablename, debug_query_table
from app.utils.app import import_blueprint
from app.utils.routes import get_file_data


def filter_from_date(
    query: "BaseQuery", cls: "Model", attr: str, from_date: datetime
) -> "BaseQuery":
    if from_date is not None:
        query = query.filter(func.date(getattr(cls, attr)) >= from_date)
    return query


def filter_to_date(
    query: "BaseQuery", cls: "Model", attr: str, to_date: datetime
) -> "BaseQuery":
    if to_date is not None:
        query = query.filter(func.date(getattr(cls, attr)) <= to_date)
    return query


def filter_order_by(
    query: "BaseQuery", cls: "Model", order_by: str, ascending: bool
) -> "BaseQuery":
    if order_by is not None:
        try:
            attr = getattr(cls, order_by)
        except:
            raise BusinessLogicException(f"Invalid property {order_by} for {cls}")
        if ascending:
            return query.order_by(attr.asc())
        else:
            return query.order_by(attr.desc())
    return query


def filter_by_user_company(query: "BaseQuery", cls: "Model") -> "BaseQuery":
    UserCompany = import_blueprint("app.api.company_users.database", "UserCompany")
    if UserCompany is not None:

        from app.api.permissions.services import PermissionService
        from app.utils.app import get_logged_user

        user = get_logged_user()

        if user and not PermissionService.is_admin(user):

            user_companies = (
                db.session.query(UserCompany.company_id)
                .filter(UserCompany.id == user.id)
                .subquery()
            )

            company_users = (
                db.session.query(UserCompany.id)
                .filter(UserCompany.company_id.in_(user_companies))
                .subquery()
            )

            return query.filter(cls.created_by_id.in_(company_users))

    return query


@convert_to_list("only", "exclude")
def generic_filters(
    _func=None,
    # This line indicates the following arguments are key-word only (https://peps.python.org/pep-3102/)
    *,
    cls=None,
    date_attr: str = "inserted_at",
    # do_from_date=True,
    from_date_attr: str = None,
    # do_to_date=True,
    to_date_attr: str = None,
    # do_order_by=True,
    only: List[str] = None,
    exclude: List[str] = None,
    skip: List[str] = None,
):
    """
    This decorator applies the from_date, to_date, and order_by filters.
    If `cls` is provided, it will be used to apply the filters, otherwise
    the decorated function should return the alias used in the query.
    If `cls` is not given, the decorator returns the alias as well.

    The `only` parameter is used to specify which filters to apply.
    The `exclude` parameter is used to specify which filters to exclude.
    If the same field is specified in both `only` and `exclude`, it will be excluded.

    The `skip` parameter is used to specify which filters to skip. Skipped filters
    will be passed to the decorated function
    """
    if from_date_attr is None:
        from_date_attr = date_attr
    if to_date_attr is None:
        to_date_attr = date_attr

    filters = {"id", "from_date", "to_date", "order_by"}
    if only is not None:
        filters = set(only)
    if exclude is not None:
        for e in exclude:
            filters.discard(e)
    if skip is not None:
        for e in skip:
            filters.discard(e)

    def decorator(f):
        @wraps(f)
        def wrapper(
            *args,
            id=None,
            from_date=None,
            to_date=None,
            order_by=None,
            ascending=None,
            **kwargs,
        ):
            use_alias = cls is None

            if skip is not None:
                if "from_date" in skip:
                    kwargs["from_date"] = from_date
                if "to_date" in skip:
                    kwargs["to_date"] = to_date
                if "order_by" in skip or "ascending" in skip:
                    kwargs["order_by"] = order_by
                    kwargs["ascending"] = ascending

            res = f(*args, **kwargs)

            if use_alias:
                q, alias = res
            else:
                q = res
                alias = cls

            if "from_date" in filters:
                q = filter_from_date(
                    query=q, cls=alias, attr=from_date_attr, from_date=from_date
                )

            if "to_date" in filters:
                q = filter_to_date(
                    query=q, cls=alias, attr=to_date_attr, to_date=to_date
                )

            if "order_by" in filters:
                q = filter_order_by(
                    query=q, cls=alias, order_by=order_by, ascending=ascending
                )

            if "id" in filters and id is not None:
                q = q.filter(alias.id == id)

            q = filter_by_user_company(q, alias)

            if use_alias:
                return q, alias
            else:
                return q

        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)

def generic_create(func=None, *, cls=None, **kwargs):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            from app.utils.database import check_mixins
            from app.utils.app import get_logged_user

            # Optional mixins mapping
            optional_mixins_modules_mapper = {
                "CanHaveTagMixin": "tags",
                "CanHaveFileMixin": "upload_files",
                "CanHaveCommentMixin": "comments",
            }

            service_to_mixin_key = {
                "TagService": "tags",
                "FileService": "upload_files",
                "CommentService": "comments"
            }

            optional_mixins_modules = {
                "app.api.tags.services": ["TagService"],
                "app.api.files.services": ["FileService"],
                "app.api.comments.services": ["CommentService"],
            }

            # Prepare placeholders for files, tags, and comments
            mixin_data = {"tags": [], "upload_files": [], "comments": []}
            mixin_services_needed = set()

            # Collect mixin data from kwargs based on the mixin presence in the class
            for mixin, mixin_arg in optional_mixins_modules_mapper.items():
                # Check if the data exists in kwargs or the mixin is relevant to the class
                if mixin_arg in kwargs or check_mixins(cls, mixin):
                    mixin_data[mixin_arg] = kwargs.pop(mixin_arg, None) or mixin_data[mixin_arg]
                    if mixin_data[mixin_arg]:  # Only process if there is relevant data
                        mixin_services_needed.add(mixin_arg)

                    # Special case for files
                    if mixin_arg == "upload_files":
                        mixin_data[mixin_arg] = get_file_data(mixin_data[mixin_arg])

            # Execute the original function
            res = f(*args, **kwargs)

            # Only import and use services if the corresponding data exists
            mixin_schemas_mapper = {}
            
            for module, services in optional_mixins_modules.items():
                for service in services:
                    mixin_key = service_to_mixin_key.get(service)
                    if mixin_key and mixin_key in mixin_services_needed:
                        # Import the service dynamically only if needed
                        mixin_schemas_mapper[mixin_key] = import_blueprint(module, service)

            # Call the relevant services based on the mixin data
            for mixin_arg, data in mixin_data.items():
                if not data:
                    continue  # Skip if no data
                
                service = mixin_schemas_mapper.get(mixin_arg)
                if not service:
                    continue  # Skip if service wasn't imported
                
                # Call the appropriate service method
                if mixin_arg == "tags":
                    service.add_tags(entity=res, tags=data)
                elif mixin_arg == "upload_files":
                    service.add_files(entity=res, user=get_logged_user(), files=data)
                elif mixin_arg == "comments":
                    service.add_comments(entity=res, comments=data)

            return res
        
        return wrapper

    # Check if `func` is passed and decorate it immediately
    if func:
        return decorator(func)
    
    return decorator

# def generic_create(
#     func=None,
#     *,
#     cls=None,
#     **kwargs,
# ):
#     """
#     This decorator creates an instance of the class `cls` with the given `kwargs`.
#     If `cls` is provided, it will be used to create the instance, otherwise
#     the decorated function should return the alias used in the query.
#     If `cls` is not given, the decorator returns the alias as well.
#     """

#     def decorator(f):
#         @wraps(f)
#         def wrapper(*args, **kwargs):

#             return f(*args, **kwargs)
#             use_alias = cls is None

#             raise Exception(use_alias)
#             # optional_mixins_modules = {
#             #     "app.api.tags.services": ["TagsService"],
#             #     "app.api.files.services": ["FileService"],
#             #     "app.api.comments.services": ["CommentService"],
#             # }

#             # optional_mixins_modules_mapper = {
#             #     "HasTagsSchemaMixin": "tags",
#             #     "HasFilesSchemaMixin": "upload_files",
#             #     "HasCommentsSchemaMixin": "comments",
#             # }

#             # # Dynamically import the services and map them to mixin arguments
#             # mixin_schemas_mapper = {}
#             # for module, services in optional_mixins_modules.items():
#             #     for service in services:
#             #         mixin_key = [
#             #             key
#             #             for key, value in optional_mixins_modules_mapper.items()
#             #             if service.lower().startswith(value.split("_")[0])
#             #         ]
#             #         if mixin_key:
#             #             mixin_schemas_mapper[
#             #                 optional_mixins_modules_mapper[mixin_key[0]]
#             #             ] = import_blueprint(module, service)

#             # from app.utils.database import check_mixins

#             # # Prepare placeholders for files, tags, and comments
#             # mixin_data = {"tags": None, "upload_files": [], "comments": None}

#             # # Collect mixin data from kwargs based on the mixin presence in the class
#             # for mixin, mixin_arg in optional_mixins_modules_mapper.items():
#             #     if check_mixins(cls, mixin):
#             #         mixin_data[mixin_arg] = (
#             #             kwargs.pop(mixin_arg, None) or mixin_data[mixin_arg]
#             #         )

#             #         if mixin_arg == "upload_files":
#             #             mixin_data[mixin_arg] = get_file_data(mixin_data[mixin_arg])

#             # Execute the main function and store the result
#             res = f(*args, **kwargs)

#             return res

#             # Dynamically call services based on the collected mixin data
#             for mixin_arg, data in mixin_data.items():
#                 service = mixin_schemas_mapper.get(mixin_arg)
#                 raise Exception(service, data)
#                 if not service or not data:
#                     continue

#                 if mixin_arg == "tags":
#                     service.add_tags(entity=res, tags=data)
#                 elif mixin_arg == "upload_files":
#                     from app.utils.app import (
#                         get_logged_user,
#                     )

#                     service.add_files(entity=res, user=get_logged_user(), files=data)
#                 elif mixin_arg == "comments":
#                     service.add_comments(entity=res, comments=data)

#             return res

#     if func is None:
#         return decorator
#     else:
#         return decorator(func)


def get_generic_entity(table_name: str, id: int) -> Type[db.Model]:
    return db.session.get(get_model_from_tablename(table_name), id)


def merge_rows_in_different_columns(
    subq,
    group_by_columns: List[str],
    discriminator_column: str,
    merge_columns: List[str],
):
    """
    This function merges different rows in the same row, splitting the different values in different columns.
    For example, given the following table:

         id | event_id | row_id |  column_name | _old_value
        265 |       98 |     10 | entity_class |      tasks
        266 |       98 |     10 |    entity_id |         15
        267 |       98 |     10 |       tag_id |          1
        271 |      100 |     11 |       tag_id |          2
        272 |      100 |     11 |    entity_id |         15
        273 |      100 |     11 | entity_class |      tasks

    and parameters:
            group_by_columns = ["event_id", "row_id"]
            discriminator_column = "column_name"
            merge_columns = ["entity_class", "entity_id"]

    The function will produce the following result:

        event_id | row_id | entity_class | entity_id
              98 |     10 |        tasks |        15
             100 |     11 |        tasks |        15

    """
    return db.session.query(
        *[getattr(subq.c, c).label(c) for c in group_by_columns],
        *[
            func.max(
                case(
                    (getattr(subq.c, discriminator_column) == c, subq.c._old_value),
                    else_=None,
                )
            ).label(c)
            for c in merge_columns
        ],
    ).group_by(*[getattr(subq.c, c) for c in group_by_columns])

 
def get_column_type(column_value):
    return type(column_value).__name__


def get_time_slots(start_date, end_date, res=1, res_unit="day"):
    """
    This function returns a query for all the timeslots between start_date and end_date.
    It is possible to control the size of each time slot with the resolution arguments
    """
    if end_date <= start_date:
        raise ImplementationException(
            f"End date ({end_date}) should be after start date ({start_date})"
        )

    hourly_series = func.generate_series(
        start_date, end_date, text(f"'{res} {res_unit}'::interval")
    ).alias("end_ts")
    lag_expression = (
        func.lag(hourly_series.column)
        .over(order_by=hourly_series.column)
        .label("start_ts")
    )
    s = db.session.query(lag_expression, hourly_series.column).subquery()
    return db.session.query(
        s.c.start_ts.label("start_ts"), s.c.end_ts.label("end_ts")
    ).filter(s.c.start_ts.is_not(None))


def get_entity_pivot_query(entity, exclude=set(["id", "inserted_at", "updated_at"])):
    """
    Given an entity, returns a query in the following format:
    | column_name | column_type | value |

    Each row then has the current value of the entity for each column
    """
    from app.utils.database import serialize_value

    # TODO: It may be either c.key or c.name
    q = union_all(
        *[
            db.session.query(
                literal(get_column_type(getattr(entity, c.key))).label("column_type"),
                literal(c.key).label("column_name"),
                literal(serialize_value(getattr(entity, c.key))).label("value"),
            )
            for c in inspect(entity.__class__).columns
            if c.key not in exclude
        ]
    ).subquery()
    q = db.session.query(q.c.column_name, q.c.column_type, q.c.value)
    # debug_query_table(q)

    return q
