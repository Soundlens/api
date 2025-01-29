def as_bool(value):
    if value:
        return value.lower() in ["true", "yes", "on", "1"]
    return False
