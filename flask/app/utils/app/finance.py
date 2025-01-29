from decimal import Decimal


def calculate_discount(initial_price: Decimal, final_price: Decimal) -> Decimal:
    """Calculate discount price. The discount value varies between 0 and 1"""

    if initial_price == 0:
        return initial_price

    return (initial_price - final_price) / initial_price


def calculate_net_price(gross_price: Decimal, vat: Decimal = Decimal('0')) -> Decimal:
    from app.exceptions import ImplementationException

    if not (0 <= vat <= 1):
        raise ImplementationException("VAT must be a number between 0 and 1")
    assert 0 <= vat <= 1
    return gross_price / (1 + vat)


def calculate_gross_price(net_price: Decimal, vat: Decimal = Decimal('0')) -> Decimal:
    from app.exceptions import ImplementationException

    if not (0 <= vat <= 1):
        raise ImplementationException("VAT must be a number between 0 and 1")
    return net_price * (1 + vat)
