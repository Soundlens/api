from datetime import date, datetime


def get_quarter(d: date) -> int:
    """Get the quarter of the year"""
    return 1 + ((d.month - 1) // 3)


def get_semester(d: date) -> int:
    """Get the semester of the year"""
    return 1 + ((d.month - 1) // 6)


def get_day_of_n_months(d: date, n: int) -> int:
    """Get the day of the n months"""
    if isinstance(d, datetime):
        d = d.date()

    n_months_start_month = ((d.month - 1) // n) * n + 1
    n_months_start_date = date(d.year, n_months_start_month, 1)
    days_diff = (d - n_months_start_date).days
    return days_diff + 1


def get_day_of_quarter(d: date) -> int:
    """Get the day of the quarter"""
    return get_day_of_n_months(d, 3)


def get_day_of_semester(d: date) -> int:
    """Get the day of the semester"""
    return get_day_of_n_months(d, 6)
