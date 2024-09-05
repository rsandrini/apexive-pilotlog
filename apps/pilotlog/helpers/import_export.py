import os
import json
import csv
import logging
from django_bulk_load import bulk_insert_models
from pilotlog.models.dynamic_table import DynamicTable

from .mappings import get_aircraft_mapping, get_flights_mapping
from .utils import convert_types, find_aircraft, write_csv_row
from apexive.settings import BULK_INSERT_CHUNK_SIZE
'''
    Import and Export ForeFlight and Logbook
    Based on ForeFlight: https://cloudfront.foreflight.com/docs/ff/16.2/ForeFlight%20Logbook.pdf
    Using references from https://support.foreflight.com/hc/en-us/articles/215647217-What-are-the-formatting-requirements-for-each-field-in-the-Logbook-template
    following the official template and JSON format exported from ForeFlight
'''

logger = logging.getLogger(__name__)


def load_data(file_path) -> json:
    """
    Load data from a file path into a JSON object.

    :param file_path: the file path to load the data from
    :return: the JSON object loaded from the file
    :raises json.JSONDecodeError: if the file path does not contain a valid JSON object
    """
    with open(file_path, 'r') as f:
        # Load as string
        data = f.read()
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            try:
                # Remove double quotes
                data = json.loads(data.replace('\\"', '"'))
            except Exception as e:
                logger.error(f"Error loading data: {e}")
                return None
        return data


def import_data(file_path):
    data = load_data(file_path)
    if not data:
        return

    objs = []
    errors = []
    batch_size = BULK_INSERT_CHUNK_SIZE

    for d in data:
        try:
            objs.append(DynamicTable(**d))
            if len(objs) >= batch_size:  # Insert in batches
                bulk_insert_models(models=objs, ignore_conflicts=True)
                objs = []  # Reset the batch
        except Exception as e:
            logger.error(f"Exception loading: {d} - {e}")
            errors.append(d)

    # Final batch insertion if there's remaining data
    if objs:
        bulk_insert_models(models=objs, ignore_conflicts=True)

    logger.info(f"Finished importing with {len(errors)} failed records.")

    if errors:
        logger.error(f"Failed records: {errors}")


def prepare_aircraft_data_to_csv(aircraft_data):
    aircraft_heads, aircraft_mapping  = get_aircraft_mapping()
    fields_aircraft_data = []
    aircraft_codes = {}

    for data in aircraft_data:
        aircraft = {}
        for key, field in aircraft_mapping.items():
            value = convert_types(data.meta.get(field, ''), key)
            aircraft[key] = value
        fields_aircraft_data.append(aircraft)
        aircraft_codes[data.guid] = data.meta.get('RefSearch', '')

    return aircraft_heads, fields_aircraft_data, aircraft_codes


def export_to_csv(file_path, aircraft_queryset=None, flight_queryset=None):
    """
    Export data from the database to a CSV file.

    :param flight_queryset:
    :param aircraft_queryset:
    :param file_path: the file path to write the data to
    :raises Exception: if there is any error during export
    """

    (aircraft_heads, fields_aircraft_data,
     flights_heads, fields_flights_data ) = prepare_logbook_data_to_csv(aircraft_queryset, flight_queryset)

    generate_csv_file(aircraft_heads,
                      fields_aircraft_data,
                      flights_heads,
                      fields_flights_data,
                      file_path)



def prepare_flights_data_to_csv(flight_data, aircraft_codes):
    flights_heads, flights_mapping = get_flights_mapping()
    fields_flights_data = []

    for data in flight_data:
        flight = {}
        for key, field in flights_mapping.items():
            value = convert_types(data.meta.get(field, ''), key)
            flight[key] = value
        flight['AircraftID'] = find_aircraft(aircraft_codes, flight['AircraftID'])
        fields_flights_data.append(flight)

    return flights_heads, fields_flights_data

def prepare_logbook_data_to_csv(aircraft_queryset=None, flight_queryset=None):
    if aircraft_queryset is None:
        aircraft_queryset = DynamicTable.objects.filter(table='Aircraft')

    if flight_queryset is None:
        flight_queryset = DynamicTable.objects.filter(table='Flight')

    aircraft_heads, fields_aircraft_data, aircraft_codes = prepare_aircraft_data_to_csv(aircraft_queryset)
    flights_heads, fields_flights_data = prepare_flights_data_to_csv(flight_queryset, aircraft_codes)

    return aircraft_heads, fields_aircraft_data, flights_heads, fields_flights_data


def generate_csv_file(aircraft_heads,
                      fields_aircraft_data,
                      flights_heads,
                      fields_flights_data,
                      file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['ForeFlight Logbook Import'] + [""] * 57)
            writer.writerow([""] * 58)

            writer.writerow(['Aircraft Table'] + [""] * 57)
            write_csv_row(writer, aircraft_heads, fields_aircraft_data)

            writer.writerow([""] * 58)
            writer.writerow(['Flights Table'])
            write_csv_row(writer, flights_heads, fields_flights_data)

        logger.info(f"CSV export complete: {file_path}")
    except (OSError, IOError) as e:
        logger.error(f"Failed to write CSV: {e}")
