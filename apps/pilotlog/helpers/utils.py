import datetime
from decimal import Decimal, InvalidOperation


def timestamp_to_year(time_string):
    try:
        # Validate that the input is a valid string and can be converted to a float or int
        timestamp = float(time_string)

        # Ensure that the timestamp is within a reasonable range
        if timestamp < 0:
            raise ValueError("Timestamp cannot be negative.")

        # Convert to a datetime object
        return datetime.datetime.fromtimestamp(timestamp).year

    except (ValueError, TypeError) as e:
        # Handle invalid inputs by logging the error or returning None
        return ''


def convert_types(value, type_expected):
    """
    Converts a value to a specific type.

    Args:
        value (object): the value to convert
        type_expected (str): the type to convert to. Supported types are:
            - 'YYYY': converts a timestamp to a year
            - 'Boolean': converts the value to a boolean, represented as 'x' or ''
            - 'Decimal': converts the value to a Decimal, or leaves it as is if it can't be converted

    Returns:
        object: the converted value
    """
    if type_expected == 'YYYY':
        value = timestamp_to_year(value)
    elif type_expected == 'Boolean':
        value = 'x' if value else ''
    elif type_expected == 'Decimal':
        try:
            value = Decimal(value)
        except (ValueError, InvalidOperation):
            pass
    return value

def find_aircraft(aircraft_codes, aircraft_id):
    for key, value in aircraft_codes.items():
        if key == aircraft_id:
            return value
    return None