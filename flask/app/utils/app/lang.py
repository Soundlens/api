import inflect
from typing import List

p = inflect.engine()


def nl_list_items(*args, richtext: bool = False, **kwargs):
    from .richtext import get_text_node

    def do_list_items(items: List[str]) -> str:
        """
        Given a list of strings, returns a natural language enumeration of the list.
        For example, given the list ["a", "b", "c"], returns "a, b and c".
        """
        if items is None:
            return []
        if len(items) <= 1:
            return items

        result = []
        for i in items[:-1]:
            result += [i, ", "]

        result += ["and ", items[-1]]

        return result

    result = do_list_items(*args, **kwargs)
    if richtext:
        return [i if type(i) != str else get_text_node(i) for i in result]
    else:
        return "".join(result)


def nl_make_plural(quantity, after) -> str:
    """
    Given a quantity, returns a string with the quantity and the appropriate pluralization.
    For example, given 1, "item", returns "1 item", and given 2, "item", returns "2 items".
    """
    return p.plural(after, quantity)
