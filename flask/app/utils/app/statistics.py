def trim_dates(parsed):
    non_empty_slots = [
        s for (s, e) in parsed if sum([v["value"] for v in parsed[(s, e)].values()]) > 0
    ]

    smallest_ts = (
        min(*non_empty_slots)
        if len(non_empty_slots) > 1
        else non_empty_slots[0]
        if len(non_empty_slots) == 1
        else None
    )

    greatest_ts = (
        max(*non_empty_slots)
        if len(non_empty_slots) > 1
        else non_empty_slots[0]
        if len(non_empty_slots) == 1
        else None
    )

    if smallest_ts is None or greatest_ts is None:
        return {}

    return {
        (s, e): {uid: u for uid, u in v.items()}
        for (s, e), v in parsed.items()
        if smallest_ts <= s <= greatest_ts
    }
