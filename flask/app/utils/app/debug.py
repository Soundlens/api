import json
from inspect import isclass
from sqlalchemy import inspect, case, literal
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.selectable import CTE, Subquery

# from sqlalchemy.sql.cte import CTE


def convert_cte_to_query(f):
    def wrapper(query, *args, **kwargs):
        if isinstance(query, CTE):
            from app import db

            query = db.session.query(*query.c)
        return f(query, *args, **kwargs)

    return wrapper


def convert_subquery_to_query(f):
    def wrapper(query, *args, **kwargs):
        if isinstance(query, Subquery):
            from app import db

            query = db.session.query(*query.c)
        return f(query, *args, **kwargs)

    return wrapper


@convert_cte_to_query
@convert_subquery_to_query
def debug_query_table(
    query,
    exclude=None,
    only=None,
    col_order=None,
    col_sep=" | ",
    print_schema=False,
    file=None,
):
    col_names = []
    for c in query.column_descriptions:
        if isclass(c["type"]):
            col_names.extend([c.name for c in inspect(c["type"]).columns])
        else:
            col_names.append(c["name"])

    # filter
    filtered_headers = set(col_names)
    if exclude is not None:
        filtered_headers = filtered_headers - set(exclude)
    if only is not None:
        filtered_headers = filtered_headers & set(only)
    if col_order is not None:
        filtered_headers = filtered_headers & set(col_order)
        col_order = [c for c in col_order if c in filtered_headers]
    else:
        col_order = [c for c in col_names if c in filtered_headers]

    col_max_len = {h: len(h) for h in filtered_headers}

    def get_row_data(row):
        if (
            len(query.column_descriptions) == 1
            and query.column_descriptions[0]["type"] == row.__class__
        ):
            # Had to use this line to get the row data in queries where the
            # row is a single class column
            return {c: getattr(row, c) for c in col_order}
        else:
            # This query is used when there are classes as a single column with other columns (e.g. db.session.query(Plant, Batch.id))
            row_data = {}
            for c in query.column_descriptions:
                if isclass(c["type"]):
                    e = getattr(row, c["name"])
                    row_data.update(
                        {c.name: getattr(e, c.name) for c in inspect(c["type"]).columns}
                    )
                else:
                    row_data.update({c["name"]: getattr(row, c["name"])})
            return row_data

    if print_schema:
        print("Query schema:", file=file)
        [
            print(f"{c['name']}: {c['type']}", file=file)
            for c in query.column_descriptions
        ]

    rows = [get_row_data(r) for r in query]
    for row_data in rows:
        for attr in filtered_headers:
            v = row_data.get(attr, "--")
            col_max_len[attr] = max(col_max_len[attr], len(str(v)))

    print(
        col_sep.join([attr.rjust(col_max_len[attr], " ") for attr in col_order]),
        file=file,
    )
    for row_data in rows:
        print(
            col_sep.join(
                [
                    str(row_data.get(attr, "--")).rjust(col_max_len[attr], " ")
                    for attr in col_order
                ]
            ),
            file=file,
        )
    print("", flush=True, file=file)


def debug_template_planned_dates_query(q):
    from app import db

    subq = q.subquery()
    readable_is_before = case(
        (subq.c.is_before == True, literal("before")),
        (subq.c.is_before == False, literal("after")),
        else_=None,
    )
    debug_query_table(
        db.session.query(
            subq.c.id.label("id"),
            subq.c.context_type.label("ct"),
            subq.c.context_id.label("cid"),
            subq.c.subject_attribute.label("sa"),
            subq.c.subject_full_path.label("sfp"),
            subq.c.subject_path.label("sp"),
            # subq.c.subject_path_len.label("spl"),
            subq.c.delta.label("d"),
            subq.c.delta_unit.label("du"),
            readable_is_before.label("ib"),
            subq.c.other_attribute.label("oa"),
            subq.c.other_full_path.label("ofp"),
            subq.c.other_path.label("op"),
            # subq.c.context_path.label("cp"),
        ).order_by(
            subq.c.subject_full_path,  # longest subject full path first
            subq.c.subject_attribute.desc(),  # start before end
            # subq.c.subject_path_len.desc(),  # longest subject path first
        ),
        # print_schema=True,
    )


@convert_cte_to_query
@convert_subquery_to_query
def debug_query(query, prefix="A" * 100):
    print(
        prefix,
        query.statement.compile(compile_kwargs={"literal_binds": True}),
        flush=True,
    )


def debug_subquery_columns(subquery, prefix="A" * 100):
    # I know it is redundant, but this way we don't need to remember
    # how to access these columns
    print(prefix, subquery.columns, flush=True)


def debug_instrumented_list(obj):
    query = Query(obj.__class__).with_entities(obj.__class__.tag_association)
    statement = query.statement.compile(compile_kwargs={"literal_binds": True})
    print(statement, flush=True)
    return statement


def debug_session_state(session):
    deleted = len(session.deleted) > 0
    new = len(session.new) > 0
    modified = any(session.is_modified(obj) for obj in session.dirty)
    letter = lambda b: "T" if b else "F"
    print(" " * 10, f"[{letter(new)}] New: {session.new}", flush=True)
    print(
        " " * 10,
        f"[{letter(modified)}] Modified: {session.dirty}",
        flush=True,
    )
    print(
        " " * 10,
        f"[{letter(deleted)}] Deleted: {session.deleted}",
        flush=True,
    )


def debug_json(j):
    print(json.dumps(j, indent=4, default=lambda x: str(x)), flush=True)
