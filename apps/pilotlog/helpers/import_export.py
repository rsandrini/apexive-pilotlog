import os
import json
import csv
import logging
from django_bulk_load import bulk_insert_models
from pilotlog.models.aircraft import Aircraft
from pilotlog.models.flight import Flight
from pilotlog.models.image_pic import ImagePic
from pilotlog.models.limit_rules import LimitRules
from pilotlog.models.my_query import MyQuery
from pilotlog.models.my_query_build import MyQueryBuild
from pilotlog.models.pilot import Pilot
from pilotlog.models.qualification import Qualification
from pilotlog.models.setting_config import SettingConfig

from .mappings import get_aircraft_mapping, get_flights_mapping
from .utils import convert_types, write_csv_row
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
    """
    Import data from a file path into the database.

    The function takes a file path as parameter, loads the data from it, and
    imports it into the database using bulk inserts. If any errors occur during
    the import, it logs the errors and continues with the next records.

    :param file_path: the file path to load the data from
    :return: None
    :raises Exception: if any error occurs during the import
    """
    data = load_data(file_path)
    if not data:
        return

    batch_size = BULK_INSERT_CHUNK_SIZE
    errors = []

    # Dictionary to hold objects for each table
    objects_map = {
        'Aircraft': [],
        'Flight': [],
        'ImagePic': [],
        'LimitRules': [],
        'MyQuery': [],
        'MyQueryBuild': [],
        'SettingConfig': [],
        'Qualification': [],
        'Pilot': [],
    }

    def insert_batch(model_name, objects):
        """
        Helper function to bulk insert objects and reset the list.

        :param model_name: the name of the model to insert
        :param objects: the list of objects to insert
        """
        if objects:
            bulk_insert_models(models=objects, ignore_conflicts=model_name != 'Aircraft')
            objects_map[model_name] = []  # Reset the list

    def process_aircraft(d):
        """
        Process an Aircraft record from the loaded data.

        :param d: a dictionary representing the Aircraft record
        """
        aircraft = d.copy()
        aircraft.pop('table')
        objects_map['Aircraft'].append(Aircraft(**aircraft))
        if len(objects_map['Aircraft']) >= batch_size:
            insert_batch('Aircraft', objects_map['Aircraft'])

    def process_flight(d):
        """
        Process a Flight record from the loaded data.

        :param d: a dictionary representing the Flight record
        """
        d.pop('table')
        try:
            aircraft = Aircraft.objects.get(guid=d['meta']['AircraftCode'])
            objects_map['Flight'].append(Flight(aircraft=aircraft, **d))
            if len(objects_map['Flight']) >= batch_size:
                insert_batch('Flight', objects_map['Flight'])
        except Aircraft.DoesNotExist as e:
            logger.error(f"Aircraft not found for Flight: {d['meta']['AircraftCode']} - {e}")
            errors.append(d)

    def process_generic(table_name, model_class, d):
        """
        Process a generic record from the loaded data.
        Generic records are any record that is not an Aircraft or Flight.

        :param table_name: the name of the table to insert into
        :param model_class: the model class to use for the insert
        :param d: a dictionary representing the record
        """
        d.pop('table')
        objects_map[table_name].append(model_class(**d))
        if len(objects_map[table_name]) >= batch_size:
            insert_batch(table_name, objects_map[table_name])

    processing_map = {
        'Aircraft': process_aircraft,
        'Flight': process_flight,
        'imagepic': lambda d: process_generic('ImagePic', ImagePic, d),
        'LimitRules': lambda d: process_generic('LimitRules', LimitRules, d),
        'myQuery': lambda d: process_generic('MyQuery', MyQuery, d),
        'myQueryBuild': lambda d: process_generic('MyQueryBuild', MyQueryBuild, d),
        'SettingConfig': lambda d: process_generic('SettingConfig', SettingConfig, d),
        'Qualification': lambda d: process_generic('Qualification', Qualification, d),
        'Pilot': lambda d: process_generic('Pilot', Pilot, d),
    }

    # Process Aircrafts first
    for d in data:
        try:
            if d['table'] == 'Aircraft':
                processing_map['Aircraft'](d)
        except Exception as e:
            logger.error(f"Exception loading Aircraft: {d} - {e}")
            errors.append(d)

    # Insert remaining Aircrafts if any
    insert_batch('Aircraft', objects_map['Aircraft'])

    # Process the rest (Flights, ImagePics, LimitRules, MyQueries)
    for d in data:
        try:
            table = d['table']
            if table != 'Aircraft' and table in processing_map:
                processing_map[table](d)
        except Exception as e:
            logger.error(f"Exception loading: {d} - {e}")
            errors.append(d)

    # Insert remaining data
    for table, objs in objects_map.items():
        insert_batch(table, objs)

    logger.info(f"Finished importing with {len(errors)} failed records.")

    if errors:
        logger.error(f"Failed records: {errors}")


def prepare_aircraft_data_to_csv(aircraft_data):
    """
    Prepare aircraft data for export to CSV.

    :param aircraft_data: a list of DynamicTable objects with table='Aircraft'
    :return: a tuple of three elements:
        1. a list of strings, which are the headers for the CSV file
        2. a list of dictionaries, where each dictionary represents a row in the CSV file
        3. a dictionary mapping each aircraft GUID to its RefSearch value
    """
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
    """
    Prepare flight data for export to CSV.

    :param flight_data: a list of DynamicTable objects with table='Flight'
    :param aircraft_codes: a dictionary mapping aircraft GUID to RefSearch
    :return: a tuple of two elements:
        1. a list of strings, which are the headers for the CSV file
        2. a list of dictionaries, where each dictionary represents a row in the CSV file
    """
    flights_heads, flights_mapping = get_flights_mapping()
    fields_flights_data = []

    for data in flight_data:
        flight = {}
        for key, field in flights_mapping.items():
            value = convert_types(data.meta.get(field, ''), key)
            flight[key] = value
        flight['AircraftID'] = aircraft_codes.get(flight['AircraftID'], '')
        fields_flights_data.append(flight)

    return flights_heads, fields_flights_data

def prepare_logbook_data_to_csv(aircraft_queryset=None, flight_queryset=None):
    """
    Prepare aircraft and flight data for export to CSV.

    :param aircraft_queryset: a queryset of DynamicTable objects with table='Aircraft'
    :param flight_queryset: a queryset of DynamicTable objects with table='Flight'
    :return: a tuple of four elements:
        1. a list of strings, which are the headers for the aircraft CSV file
        2. a list of dictionaries, where each dictionary represents a row in the aircraft CSV file
        3. a list of strings, which are the headers for the flights CSV file
        4. a list of dictionaries, where each dictionary represents a row in the flights CSV file
    """
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
    """
    Write aircraft and flight data to a CSV file.

    This function takes the data prepared by prepare_logbook_data_to_csv and
    writes it to a CSV file.

    :param aircraft_heads: a list of strings, which are the headers for the aircraft CSV file
    :param fields_aircraft_data: a list of dictionaries, where each dictionary represents a row in the aircraft CSV file
    :param flights_heads: a list of strings, which are the headers for the flights CSV file
    :param fields_flights_data: a list of dictionaries, where each dictionary represents a row in the flights CSV file
    :param file_path: the file path to write the data to
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['ForeFlight Logbook Import'])
            writer.writerow([""])

            writer.writerow(['Aircraft Table'])
            write_csv_row(writer, aircraft_heads, fields_aircraft_data)

            writer.writerow([""])
            writer.writerow(['Flights Table'])
            write_csv_row(writer, flights_heads, fields_flights_data)

        logger.info(f"CSV export complete: {file_path}")
    except (OSError, IOError) as e:
        logger.error(f"Failed to write CSV: {e}")