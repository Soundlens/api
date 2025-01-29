from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, rruleset, DAILY, HOURLY, MO, TU, WE, TH, FR

from decimal import Decimal
from typing import List

from app.exceptions import ImplementationException
from app.utils.app.enum import Enum


def is_in_interval(date, start, end):
    return start <= date <= end


class RelativeDateUnit(Enum):
    YEAR = "year"
    MONTH = "month"
    WEEK = "week"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"
    SECOND = "second"


def get_relativedelta(delta: float, delta_unit: RelativeDateUnit) -> relativedelta:
    from app.exceptions import ImplementationException

    kwargs = {}
    match delta_unit:
        case RelativeDateUnit.YEAR:
            kwargs = {"years": delta}
        case RelativeDateUnit.MONTH:
            kwargs = {"months": delta}
        case RelativeDateUnit.WEEK:
            kwargs = {"weeks": delta}
        case RelativeDateUnit.DAY:
            kwargs = {"days": delta}
        case RelativeDateUnit.HOUR:
            kwargs = {"hours": delta}
        case RelativeDateUnit.MINUTE:
            kwargs = {"minutes": delta}
        case RelativeDateUnit.SECOND:
            kwargs = {"seconds": delta}
        case _:
            raise ImplementationException(f"Invalid delta_unit: {delta_unit}")
    return relativedelta(delta, **kwargs)


def get_relative_date_timedelta(
    delta: float, delta_unit: RelativeDateUnit
) -> relativedelta:
    from app.exceptions import ImplementationException

    match delta_unit:
        case RelativeDateUnit.YEAR:
            return timedelta(days=delta * 365)
        case RelativeDateUnit.MONTH:
            return timedelta(days=delta * 30)
        case RelativeDateUnit.WEEK:
            return timedelta(weeks=delta)
        case RelativeDateUnit.DAY:
            return timedelta(days=delta)
        case RelativeDateUnit.HOUR:
            return timedelta(hours=delta)
        case RelativeDateUnit.MINUTE:
            return timedelta(minutes=delta)
        case RelativeDateUnit.SECOND:
            return timedelta(seconds=delta)
        case _:
            raise ImplementationException(f"Invalid delta_unit: {delta_unit}")


def get_n_working_days(
    base_date: datetime,
    n: int,
    is_before: bool = False,
    working_days: List = [MO, TU, WE, TH, FR],
    exdates: List[datetime] = [],
    # exrules=[], # not working yet...
) -> List[datetime]:
    """
    Returns the list of the next/previous working days after/before base_date,
    excluding base_date.
    """
    if n == 0:
        raise ImplementationException("Cannot get 0 business days after a day")

    ## Step 1: Get the day window that will contain
    ## all the n working days before/after base_date
    ## We are assuming that in any window range, at least
    ## half of the days are working days
    window_size = max(10, n * 2)
    d = relativedelta(days=window_size)
    if is_before:
        s = base_date - d
        e = base_date
    else:
        s = base_date
        e = base_date + d

    # print(f"Getting {n} working days {'before' if is_before else 'after'} {base_date}", flush=True)
    # print(" "*4, f"Using range [{s}, {e}]", flush=True)

    ## Step 2: Setup working day rules
    rules = rruleset()
    rules.rrule(rrule(DAILY, dtstart=s, until=e, byweekday=working_days))
    for d in exdates:
        rules.exdate(d)
    # for r in exrules:
    #     rules.exrule(r)

    ## Step 3: Get n days before/after the base_date
    ## The inc argument specifies if we want to include the rule start
    ## (given by the variable s) in these results.
    ## If we are getting the n work days AFTER the base_date, we want to
    ##   exclude s (which will correspond to base_date)
    ## If we are getting the n work days BEFORE the base_date, we want to
    ##   include s
    working_days = list(rules.xafter(s, inc=is_before))
    assert len(working_days) > n
    # [print(i, d) for i, d in enumerate(working_days)]
    if is_before:
        ## Get the n first days before base_date
        ## Since xafter does not have any parameter to exclude the
        ## last date, we need to check if manually
        if base_date == working_days[-1]:
            return working_days[-n - 1 : -1]
        else:
            return working_days[-n:]
    else:
        ## Get the n first days after base_date
        ## (base_date is already excluded)
        return working_days[:n]


def get_nth_working_day(base_date: datetime, n: int, is_before: bool = False, **kwargs):
    """
    Returns the nth working day after/before base_date, excluding base_date.
    """
    working_days = get_n_working_days(
        base_date=base_date, n=n, is_before=is_before, **kwargs
    )
    if is_before:
        result = working_days[0]
    else:
        result = working_days[-1]
    # print(
    #     f"{n} working days {'before' if is_before else 'after '} {base_date}: {result}"
    # )
    return result


def calculate_relative_date(
    base_date: datetime,
    delta: float,
    delta_unit: RelativeDateUnit,
    is_before: bool,
    ignore_holidays: bool,
) -> datetime:
    d = get_relativedelta(delta, delta_unit)
    if is_before:
        d = -d

    if ignore_holidays:
        # TODO: how to account only for work-time hours?
        # TODO: pass public holidays
        n_work_days = d.days
        if -1 < n_work_days < 1:
            # We want to get the next/previous working day of base_date +- delta
            target = base_date + d
            # Apply rule to filter out invalid targets
            s = target - relativedelta(days=10) if is_before else target
            rset = rruleset()
            rset.rrule(
                rrule(
                    dtstart=s,
                    freq=HOURLY,
                    byhour=[8, 9, 10, 11, 12, 13, 14, 15, 16],
                    byminute=[0],
                    byweekday=[MO, TU, WE, TH, FR],
                ),
                # rrule(dtstart=target, freq=YEARLY, byweekday=[MO, TU, WE, TH, FR])
            )
            # If
            if is_before:
                result = rset.before(target, inc=True)
            else:
                result = rset.after(target, inc=True)
        else:
            result = get_nth_working_day(
                base_date=base_date, n=int(n_work_days), is_before=is_before
            )
    else:
        result = base_date + d
    return result
