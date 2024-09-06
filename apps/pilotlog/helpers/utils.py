import logging
import datetime
import json
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)


def timestamp_to_year(time_string):
    """
    Converts a timestamp string to a year.

    Args:
        time_string (str): A string containing a timestamp in seconds since the epoch.

    Returns:
        int: The year that the timestamp corresponds to, or None if the input is invalid.
    """
    try:
        # Validate that the input is a valid string and can be converted to a float or int
        timestamp = float(time_string)

        # Ensure that the timestamp is within a reasonable range
        if timestamp < 0:
            raise ValueError("Timestamp cannot be negative.")

        # Convert to a datetime object
        dt = datetime.datetime.fromtimestamp(timestamp)

        # Return the year
        return dt.year

    except (ValueError, TypeError) as e:
        # Handle invalid inputs by logging the error and returning None
        logger.error(f"Error converting timestamp to year: {e}")
        return None


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


def write_csv_row(writer, headers, data):
    """
    Utility function to write headers and corresponding data rows to CSV.

    Args:
        writer (csv.writer): a CSV writer object
        headers (list): a list of strings, which are the headers for the CSV file
        data (list): a list of dictionaries, where each dictionary represents a row in the CSV file
    """
    if not data:
        logger.warning("No data to write.")
        return

    # Write the headers
    writer.writerow(headers)

    # Write the header names
    writer.writerow(key for key in data[0].keys())

    # Write the data rows
    for row in data:
        writer.writerow(row.values())


def load_mappings(mapping_file):
    """
    Load field mappings from a JSON or YAML file to allow future configurability.

    The mapping file should contain a dictionary where the keys are the
    source field names and the values are the corresponding target field names.
    """
    with open(mapping_file) as f:
        # Load the mappings from the file
        mappings = json.load(f)

        # Check that the mappings are a dictionary
        if not isinstance(mappings, dict):
            raise ValueError("Mappings must be a dictionary")

        # Check that the dictionary values are strings
        for key, value in mappings.items():
            if not isinstance(value, str):
                raise ValueError(f"Mapping value for {key} must be a string")

        return mappings
