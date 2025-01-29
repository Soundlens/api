from typing import List
from decimal import Decimal
from datetime import timedelta
from app.utils.app.enum import Enum
from app.exceptions import ImplementationException, UnitException
from sqlalchemy import case, cast, String


class UnitType(Enum):
    UNITLESS = "unitless"
    MASS = "mass"
    VOLUME = "volume"
    LENGTH = "length"
    AREA = "area"
    ENERGY = "energy"
    POWER = "power"
    LUMINOSITY = "luminosity"
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    FREQUENCY = "frequency"
    PH = "pH"
    TIME = "time"
    PERCENTAGE = "percentage"


class Unit(Enum):
    """
    Contains every possible unit represented in this project
    """

    # Unitless
    UNIT = "unit"
    PERCENTAGE = "%"

    # Mass
    Kg = "Kg"
    g = "g"
    mg = "mg"

    # Volume
    KL = "KL"
    L = "L"
    ml = "ml"

    # Length
    KM = "km"
    M = "m"
    CM = "cm"
    MM = "mm"

    # Area
    M2 = "m2"
    CM2 = "cm2"
    MM2 = "mm2"

    # Power
    KW = "KW"
    W = "W"

    # Energy
    KWH = "KWH"
    WH = "WH"

    # time
    WEEK = "week"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"
    SECOND = "second"

    # Luminosity
    LUMEN = "lumen"

    # Temperature
    CELSIUS = "C"
    FAHRENHEIT = "F"
    KELVIN = "kelvin"

    # Pressure
    hPa = "hPa"
    Pa = "Pa"
    BAR = "bar"

    # Frequency
    HZ = "Hz"

    # pH
    PH = "pH"


"""
Associates a list of units to its corresponding unit type
"""
TYPE_UNITS = {
    UnitType.UNITLESS: [Unit.UNIT],
    UnitType.MASS: [Unit.Kg, Unit.g, Unit.mg],
    UnitType.VOLUME: [Unit.KL, Unit.L, Unit.ml],
    UnitType.LENGTH: [Unit.KM, Unit.M, Unit.CM, Unit.MM],
    UnitType.AREA: [Unit.M2, Unit.CM2, Unit.MM2],
    UnitType.POWER: [Unit.KW, Unit.W],
    UnitType.ENERGY: [Unit.KWH, Unit.WH],
    UnitType.TIME: [Unit.WEEK, Unit.DAY, Unit.HOUR, Unit.MINUTE, Unit.SECOND],
    UnitType.LUMINOSITY: [Unit.LUMEN],
    UnitType.TEMPERATURE: [Unit.CELSIUS, Unit.FAHRENHEIT, Unit.KELVIN],
    UnitType.PRESSURE: [Unit.hPa, Unit.Pa, Unit.BAR],
    UnitType.FREQUENCY: [Unit.HZ],
    UnitType.PH: [Unit.PH],
    UnitType.PERCENTAGE: [Unit.PERCENTAGE],
}

"""
Associates the unit type to each unit. This is just the reverse of TYPE_UNITS
"""
UNIT_TYPE = {u: k for k, v in TYPE_UNITS.items() for u in v}


# ------------------
# Compatibility
# ------------------
UNCONVERTIBLE_TYPES = [UnitType.UNITLESS, UnitType.PH]


def get_unit_type(unit: Unit) -> UnitType:
    """
    Returns the UnitType of a given unit
    """
    if unit not in UNIT_TYPE:
        raise ImplementationException(f"Unit {unit} not present in type mapping")
    return UNIT_TYPE[unit]


def get_type_units(unit_type: UnitType) -> List[Unit]:
    """
    Returns all the units of a given UnitType
    """
    if unit_type not in TYPE_UNITS:
        raise ImplementationException(
            f"Unit type {unit_type} not present in type mapping"
        )
    return TYPE_UNITS[unit_type]


def get_compatible_units(u: Unit) -> List[Unit]:
    """
    Returns all the units of the same type as the given unit
    """
    unit_type = get_unit_type(u)
    if unit_type in UNCONVERTIBLE_TYPES:
        return [u]
    else:
        return get_type_units(unit_type)


def check_compatible(u1: Unit, u2: Unit) -> bool:
    """
    Two units are compatible if we can convert from one to the other.
    Returns True if the two units are compatible, False otherwise.
    """
    return u2 in get_compatible_units(u1)


def get_biggest_unit_in_family_for_unit(unit: Unit, family: list[Unit]) -> Unit:
    # first i need to filter the family to only include units that are compatible with the given unit
    compatible_units = [{u: SI[u]} for u in family if check_compatible(u, unit)]

    # then i need to sort the units by their SI value
    sorted_units = sorted(compatible_units, key=lambda x: x[list(x.keys())[0]])

    # then i need to get the last unit in the list
    return list(sorted_units[-1].keys())[0]


def get_timedelta_for_unit(value, unit: Unit) -> timedelta:
    if unit == Unit.WEEK:
        return timedelta(weeks=int(value))
    elif unit == Unit.DAY:
        return timedelta(days=int(value))
    elif unit == Unit.HOUR:
        return timedelta(hours=int(value))
    elif unit == Unit.MINUTE:
        return timedelta(minutes=int(value))
    elif unit == Unit.SECOND:
        return timedelta(seconds=int(value))
    else:
        raise UnitException(description=f"Cannot convert {unit} to timedelta")


# ------------------
# Canonical Units
# ------------------
CANONICAL_UNITS = {
    UnitType.MASS: Unit.mg,
    UnitType.VOLUME: Unit.ml,
    UnitType.LENGTH: Unit.MM,
    UnitType.AREA: Unit.MM2,
    UnitType.POWER: Unit.W,
    UnitType.ENERGY: Unit.WH,
    UnitType.TIME: Unit.SECOND,
    UnitType.LUMINOSITY: Unit.LUMEN,
    UnitType.TEMPERATURE: Unit.CELSIUS,
    UnitType.PRESSURE: Unit.BAR,
    UnitType.FREQUENCY: Unit.HZ,
    UnitType.PH: Unit.PH,
    UnitType.PERCENTAGE: Unit.PERCENTAGE,
}


def get_canonical_unit(unit: Unit) -> Unit:
    unit_type = get_unit_type(unit)
    if unit_type in UNCONVERTIBLE_TYPES:
        return unit

    if unit_type not in CANONICAL_UNITS:
        raise ImplementationException(
            f"Unit type {unit_type} not present in canonical mapping"
        )

    return CANONICAL_UNITS[unit_type]


CANONICAL_UNIT_MAPPING = {u.value: get_canonical_unit(u).value for u in Unit}


def get_canonical_unit_expression(column):
    return case(
        CANONICAL_UNIT_MAPPING,
        value=column,
        else_="ERROR",
    )


# ------------------
# Conversion
# ------------------
SI = {
    Unit.UNIT: Decimal("1"),
    Unit.PERCENTAGE: Decimal("1"),
    #
    # Mass
    Unit.Kg: Decimal("1000000"),
    Unit.g: Decimal("1000"),
    Unit.mg: Decimal("1"),
    #
    # Volume
    Unit.KL: Decimal("1000000"),
    Unit.L: Decimal("1000"),
    Unit.ml: Decimal("1"),
    #
    # Length
    Unit.KM: Decimal("1000000"),
    Unit.M: Decimal("1000"),
    Unit.CM: Decimal("10"),
    Unit.MM: Decimal("1"),
    #
    # Area
    Unit.M2: Decimal("1000000"),
    Unit.CM2: Decimal("100"),
    Unit.MM2: Decimal("1"),
    #
    # Power
    Unit.KW: Decimal("1000"),
    Unit.W: Decimal("1"),
    #
    # Energy
    Unit.KWH: Decimal("1000"),
    Unit.WH: Decimal("1"),
    #
    # Time
    Unit.WEEK: Decimal("604800"),
    Unit.DAY: Decimal("86400"),
    Unit.HOUR: Decimal("3600"),
    Unit.MINUTE: Decimal("60"),
    Unit.SECOND: Decimal("1"),
    #
    # Luminosity
    Unit.LUMEN: Decimal("1"),
    #
    # Temperature
    # Temperature needs a custom conversion function
    #
    # Pressure
    Unit.BAR: Decimal("100000"),
    Unit.hPa: Decimal("100"),
    Unit.Pa: Decimal("1"),
    #
    # Frequency
    Unit.HZ: Decimal("1"),
    #
    # pH
    Unit.PH: Decimal("1"),
}


def convert_unit(
    value: Decimal, unit_in: Unit, unit_out: Unit, inversely_proportional: bool = False
) -> Decimal:
    """Converts a given value from an initial unit to a target unit.
    If inversely_proportional is set to True, this function assumes that the conversion
    is being done between 1/unit_in and 1/unit_out.
    """

    if unit_in == unit_out:
        return value

    if not check_compatible(unit_in, unit_out):
        raise UnitException(f"Cannot convert {unit_in} to {unit_out}", code=500)

    unit_type = get_unit_type(unit_in)
    if unit_type == UnitType.TEMPERATURE:
        from .convert_temperatures import c_to_f, c_to_k, f_to_c, f_to_k, k_to_c, k_to_f

        mapping = {
            (Unit.CELSIUS, Unit.FAHRENHEIT): c_to_f,
            (Unit.CELSIUS, Unit.KELVIN): c_to_k,
            (Unit.FAHRENHEIT, Unit.CELSIUS): f_to_c,
            (Unit.FAHRENHEIT, Unit.KELVIN): f_to_k,
            (Unit.KELVIN, Unit.CELSIUS): k_to_c,
            (Unit.KELVIN, Unit.FAHRENHEIT): k_to_f,
        }
        if inversely_proportional:
            raise ImplementationException(
                "Cannot determine how to convert temperatures when inversely proportional"
            )
        key = (unit_in, unit_out)
        if key not in mapping:
            raise ImplementationException("Missing temperature conversion function")
        return mapping[key](value)

    ratio = SI[unit_in] / SI[unit_out]
    if inversely_proportional:
        ratio = 1 / ratio
    if isinstance(value, float):
        value = Decimal(str(value))
    if isinstance(ratio, float):
        ratio = Decimal(str(ratio))
    return value * ratio


def convert_to_appropriate_unit(
    value: Decimal, unit_in: Unit, inversely_proportional: bool = False
) -> tuple[Decimal, Unit]:
    """
    If inversely_proportional is set to True, this function assumes that the conversion
    is being done between 1/unit_in and 1/appropriate_unit.
    """
    if value < 0:
        v, u = convert_to_appropriate_unit(-value, unit_in)
        return -v, u

    best_value = value
    best_unit = unit_in

    for unit_out in get_compatible_units(unit_in):
        value_attempt = convert_unit(
            value, unit_in, unit_out, inversely_proportional=inversely_proportional
        )
        # Left these if statements broken up for readability:
        # If the best value is smaller than 1, we want values higher than it
        # (even if they are waaay larger)
        if best_value < 1:
            if value_attempt > best_value:
                best_value = value_attempt
                best_unit = unit_out

        # If the best_value is already > 1, we only want to update it
        # if there is a value greater than 1 but smaller than it
        else:
            if 1 <= value_attempt < best_value:
                best_value = value_attempt
                best_unit = unit_out
    return best_value, best_unit


def convert_to_canonical_unit(
    quantity: Decimal, unit: Unit, inversely_proportional: bool = False
) -> tuple[Decimal, Unit]:
    """
    If inversely_proportional is set to True, this function assumes that the conversion
    is being done between 1/unit_in and 1/canonical_unit.
    """
    canonical_unit = get_canonical_unit(unit)
    return (
        convert_unit(
            quantity,
            unit,
            canonical_unit,
            inversely_proportional=inversely_proportional,
        ),
        canonical_unit,
    )


# ------------------
# Comparison
# ------------------
def eq(v1: Decimal, u1: Unit, v2: Decimal, u2: Unit) -> bool:
    v2 = convert_unit(v2, u2, u1)
    return v1 == v2


def ne(v1: Decimal, u1: Unit, v2: Decimal, u2: Unit) -> bool:
    return not eq(v1, u1, v2, u2)


def gt(v1: Decimal, u1: Unit, v2: Decimal, u2: Unit) -> bool:
    v2 = convert_unit(v2, u2, u1)
    return v1 > v2


def ge(v1: Decimal, u1: Unit, v2: Decimal, u2: Unit) -> bool:
    v2 = convert_unit(v2, u2, u1)
    return v1 >= v2


def lt(v1: Decimal, u1: Unit, v2: Decimal, u2: Unit) -> bool:
    return gt(v2, u2, v1, u1)


def le(v1: Decimal, u1: Unit, v2: Decimal, u2: Unit) -> bool:
    return ge(v2, u2, v1, u1)


# ------------------
# Addition/subtraction
# ------------------
def add_measurements(v1: Decimal, u1: Unit, v2: Decimal, u2: Unit, u3: Unit) -> Decimal:
    if not check_compatible(u1, u2):
        raise UnitException(description=f"{u1} and {u2} are not compatible", code=400)
    if not check_compatible(u1, u3) or not check_compatible(u2, u3):
        raise UnitException(description=f"Cannot convert input units to {u3}")

    v1 = convert_unit(v1, u1, u3)
    v2 = convert_unit(v2, u2, u3)
    return Decimal(v1) + Decimal(v2)


def subtract_measurements(
    v1: Decimal, u1: Unit, v2: Decimal, u2: Unit, u3: Unit
) -> Decimal:
    return add_measurements(v1, u1, -v2, u2, u3)


# ------------------
# Strings
# ------------------
UNIT_REPRESENTATION = {
    Unit.UNIT: "unit",
    Unit.PERCENTAGE: "%",
    # mass
    Unit.Kg: "kg",
    Unit.g: "g",
    Unit.mg: "mg",
    # volume
    Unit.KL: "kL",
    Unit.L: "L",
    Unit.ml: "ml",
    # Length
    Unit.KM: "km",
    Unit.M: "m",
    Unit.CM: "cm",
    Unit.MM: "mm",
    # area
    Unit.M2: "m²",
    Unit.CM2: "cm²",
    Unit.MM2: "mm²",
    # power
    Unit.KW: "kW",
    Unit.W: "W",
    # energy
    Unit.KWH: "kWh",
    Unit.WH: "Wh",
    # time
    Unit.WEEK: "week",
    Unit.DAY: "day",
    Unit.HOUR: "hour",
    Unit.MINUTE: "minute",
    Unit.SECOND: "second",
    # luminosity
    Unit.LUMEN: "lumen",
    # temperature
    Unit.CELSIUS: "ºC",
    Unit.FAHRENHEIT: "ºF",
    Unit.KELVIN: "K",
    # pressure
    Unit.hPa: "hPa",
    Unit.Pa: "Pa",
    Unit.BAR: "bar",
    # frequency
    Unit.HZ: "Hz",
    # pH - left blank intetionally because ph measurements do not have
    # a unit, they are just a number.
    Unit.PH: "",
}

REVERSED_UNIT_REPRESENTATION = {v: k for k, v in UNIT_REPRESENTATION.items()}

PLURAL_UNITS = [
    Unit.UNIT,
    Unit.WEEK,
    Unit.DAY,
    Unit.HOUR,
    Unit.MINUTE,
    Unit.SECOND,
]


TIME_ENUM_TO_TIMEDELTA = {
    Unit.SECOND: "seconds",
    Unit.MINUTE: "minutes",
    Unit.HOUR: "hours",
    Unit.DAY: "days",
    Unit.WEEK: "weeks",
}

def get_unit_string(unit: Unit) -> str:
    return UNIT_REPRESENTATION[unit]


def get_unit_from_string(string: str) -> Unit:
    return REVERSED_UNIT_REPRESENTATION[string]


def get_quantity_string(quantity, unit, decimal_places=6):
    # make plural if needed

    quantity, unit = convert_to_appropriate_unit(quantity, unit)
    unit_format = get_unit_string(unit)
    if unit in PLURAL_UNITS and (quantity > 1 or quantity == 0):
        unit_format += "s"

    qty_format = f"{quantity:.{decimal_places}f}".rstrip("0").rstrip(".")
    return f"{qty_format} {unit_format}".strip()


# ------------------
# Module assertions
# ------------------

# Assert every unit has a type
for unit in Unit.all_values():
    assert get_unit_type(unit) is not None

# Assert every type has at least one unit
for unit_type in UnitType.all_values():
    assert len(get_type_units(unit_type)) > 0

# Assert every unit type is either convertible or not
assert set(UnitType.all_values()) == set(CANONICAL_UNITS.keys()) | set(
    UNCONVERTIBLE_TYPES
)

# Assert every type has appropriate canonical unit
for unit_type in CANONICAL_UNITS:
    canon_unit = CANONICAL_UNITS[unit_type]
    assert unit_type == get_unit_type(canon_unit)

# Assert every unit has appropriate representation
for unit in Unit.all_values():
    assert unit in UNIT_REPRESENTATION

# ------------------
# Legacy code
# ------------------


def get_SI_unit(unit: Unit):
    return get_type_units(get_unit_type(unit))[0]
    # if unit in WEIGHT_UNITS:
    #     return Unit.Kg

    # if unit in VOLUME_UNITS:
    #     return Unit.L

    # if unit in [Unit.UNIT]:
    #     return Unit.UNIT


def aggregate_results_by_normalized_unit(
    results,
    aggregated_key,
    key_tuple_result,
    array_key=None,
    quantity_key="quantity",
    unit_key="unit",
):
    """
    Takes a list of results and aggregates them by the given unit, converting
    all values to that unit. This is useful for aggregating results from
    different units, such as grams and kilograms, into a single unit, such as
    kilograms.
    """

    def get_nested_attr(obj, path):
        if len(path) == 0:
            return obj
        if isinstance(obj, dict):
            return get_nested_attr(obj.get(path[0], {}), path[1:])
        else:
            return get_nested_attr(getattr(obj, path[0]), path[1:])

    def create_nested_tuple(d, path_list):
        return tuple(
            get_nested_attr(d, path if isinstance(path, tuple) else (path,))
            for path in path_list
        )

    aggregated = {}
    for entry in results:
        d = entry._asdict()
        entity_id = d.get(aggregated_key)

        key = create_nested_tuple(d, key_tuple_result)
        if key not in aggregated:
            aggregated[key] = d
            if array_key:
                aggregated[key][array_key] = (
                    [entity_id] if entity_id is not None else []
                )
        else:
            if array_key:
                if entity_id is not None:
                    aggregated[key][array_key].append(entity_id)

            sub_total = aggregated[key][quantity_key]

            sub_unit = aggregated[key][unit_key]

            quantity = d[quantity_key]
            unit = d[unit_key]
            sub_total = add_measurements(sub_total, sub_unit, quantity, unit, sub_unit)
            sub_total, sub_unit = convert_to_appropriate_unit(sub_total, sub_unit)
            aggregated[key][quantity_key] = sub_total
            aggregated[key][unit_key] = sub_unit

    return aggregated
