"""
Here we will store some functions that will be useful in migrations
"""


def rename_column_value(
    *,
    i_understand_what_this_does: bool,
    table_name: str,
    column_name: str,
    old_value: str,
    new_value: str,
    op=None,
):
    """
    This function will change the old_value to the new_value in the column_name of the table_name
    and will change the history accordingly
    """
    assert i_understand_what_this_does

    statements = [
        f"update {table_name} set {column_name} = '{new_value}' where {column_name} = '{old_value}'",
        f"update history set _new_value = '{new_value}' where history_type = 'update' and  table_name = '{table_name}' and column_name = '{column_name}' and _new_value = '{old_value}';",
        f"update history set _old_value = '{new_value}' where history_type = 'update' and  table_name = '{table_name}' and column_name = '{column_name}' and _old_value = '{old_value}';",
        f"update history set _old_value = '{new_value}' where history_type = 'delete' and  table_name = '{table_name}' and column_name = '{column_name}' and _old_value = '{old_value}';",
    ]

    for s in statements:
        print(s, flush=True)
        if op is not None:
            op.execute(s)
