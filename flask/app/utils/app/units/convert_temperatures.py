from decimal import Decimal


def c_to_f(c: Decimal) -> Decimal:
    return c * (Decimal("9.0") / Decimal("5")) + Decimal("32")


def c_to_k(c: Decimal) -> Decimal:
    return c + Decimal("273.15")


def f_to_c(f: Decimal) -> Decimal:
    return ((f - Decimal("32")) * Decimal("5.0")) / Decimal("9")


def f_to_k(f: Decimal) -> Decimal:
    return (f + Decimal("459.67")) * Decimal("5.0") / Decimal("9")


def k_to_c(k: Decimal) -> Decimal:
    return k - Decimal("273.15")


def k_to_f(k: Decimal) -> Decimal:
    return k * Decimal("9.0") / Decimal("5") - Decimal("459.67")
