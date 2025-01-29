from app import ma
from app.utils.app.units import get_quantity_string


class DecimalField(ma.Decimal):
    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        if isinstance(value, str):
            return super()._deserialize(value.replace(",", "."), attr, data, **kwargs)
        return super()._deserialize(value, attr, data, **kwargs)


class CurrencyField(DecimalField):
    def __init__(self, *args, currency="€", **kwargs):
        self.currency = currency
        super().__init__(*args, places=2, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        if isinstance(value, str):
            return super()._deserialize(
                value.replace(self.currency, ""), attr, data, **kwargs
            )
        return super()._deserialize(value, attr, data, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        value = super()._serialize(value, attr, obj, **kwargs)
        return f"{value}{self.currency}"


class FormattedQuantityField(ma.String):
    def __init__(self, quantity_key: str, unit_key: str, *args, **kwargs):
        self.quantity_key = quantity_key
        self.unit_key = unit_key

        # We can only have multiple attributes for the same field if they are dump_only
        # https://github.com/marshmallow-code/marshmallow/issues/1038
        super().__init__(*args, attribute=quantity_key, dump_only=True, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        quantity = getattr(obj, self.quantity_key, None)
        unit = getattr(obj, self.unit_key, None)
        if quantity is None or unit is None:
            return "--"
        return get_quantity_string(quantity, unit)
