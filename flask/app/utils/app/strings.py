from typing import List


def split_words(s: str) -> List[str]:
    """
    Given a string, returns the words of the string.
    For example, given "John Doe", returns ["John", "Doe"].
    """
    return s.split()


def get_initials(s: str) -> str:
    """
    Given a string, returns the initials of the string.
    For example, given "John Doe", returns "JD".
    """
    return "".join([w[0] for w in split_words(s)])


def reverse(s: str) -> str:
    """
    Given a string, returns the reverse of the string.
    For example, given "John Doe", returns "eoD nhoJ".
    """
    return s[::-1]
