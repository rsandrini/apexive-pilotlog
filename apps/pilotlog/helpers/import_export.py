import os
import json
import csv
import logging
from django_bulk_load import bulk_insert_models
from pilotlog.models.dynamic_table import DynamicTable
from .utils import convert_types, find_aircraft
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
            # Remove double quotes
            data = json.loads(data.replace('\\"', '"'))

        return data


def import_data(file_path):
    """
    Import data from a file path into the database.

    :param file_path: the file path to load the data from
    :raises json.JSONDecodeError: if the file path does not contain a valid JSON object
    :raises Exception: if there is any error during import
    """
    data = load_data(file_path)

    objs = []
    for d in data:
        try:
            objs.append(DynamicTable(**d))
        except Exception as e:
            logger.error(f"Exception loading: {d} - {e}")

    logger.info(f"Importing {len(objs)} objects")
    batch_size = BULK_INSERT_CHUNK_SIZE

    for start in range(0, len(objs), batch_size):
        batch = objs[start:start + batch_size]
        try:
            # Bulk insert using django_bulk_load, faster than django
            bulk_insert_models(
                models=batch,
                ignore_conflicts=True
            )
            logger.info(f"Batch starting at index {start} inserted "
                        f"successfully")
        except Exception as e:
            logger.error(f"Exception in import data at batch starting index "
                         f"{start}: {e}")

    logger.info(f"Imported {len(objs)} objects")


def export_to_csv(file_path):
    """
    Export data from the database to a CSV file.

    :param file_path: the file path to write the data to
    :raises Exception: if there is any error during export
    """

    (aircraft_heads, fields_aircraft_data,
     flights_heads, fields_flights_data ) = prepare_logbook_data_to_csv(None, None)

    generate_csv_file(aircraft_heads,
                      fields_aircraft_data,
                      flights_heads,
                      fields_flights_data,
                      file_path)


def prepare_aircraft_data_to_csv(aircraft_data):
    """
    Prepare the aircraft data for export to a CSV file.

    Returns a tuple with the headers and fields for the aircraft table.
    Follows the CSV template and converts the data types to the correct format.
    There are some special cases where the values are not in the template.

    :return: a tuple with the headers and fields for the aircraft table
    :rtype: tuple(list, list, list)
    """
    aircraft_heads = ['Text', 'Text', 'Text', 'YYYY', 'Text', 'Text', 'Text',
                      'Text', 'Text', 'Text', 'Boolean', 'Boolean',
                      'Boolean', 'Boolean']
    aircraft_fields = ['AircraftID', 'EquipmentType', 'TypeCode', 'Year',
                       'Make', 'Model', 'Category', 'Class', 'GearType',
                       'EngineType', 'Complex', 'HighPerformance',
                       'Pressurized', 'TAA']

    # Create a mapping of fields, key and values has the same name
    aircraft_mapping = dict(zip(aircraft_fields, aircraft_fields))
    # Overwrite values, trying to follow the docs (see links in the docstring)
    aircraft_mapping['AircraftID'] = "RefSearch"
    aircraft_mapping['Year'] = "Record_Modified"
    aircraft_mapping['HighPerformance'] = "HighPerf"
    aircraft_mapping['TAA'] = "Aerobatic"

    # Map aircraft fields from the meta-data
    fields_aircraft_data = []
    aircraft_codes = {}
    for data in aircraft_data:
        aircraft = {}
        for i, (key, field) in enumerate(aircraft_mapping.items()):
            value = convert_types(data.meta.get(field, ''), aircraft_heads[i])
            aircraft[key] = value
        fields_aircraft_data.append(aircraft)
        aircraft_codes[data.guid] = data.meta.get('RefSearch', '')
    return aircraft_heads, fields_aircraft_data, aircraft_codes


def prepare_flights_data_to_csv(flight_data, aircraft_codes):

    """
    Prepare the data for export to a CSV file.

    Returns a tuple with the headers and fields for the flights table.
    Follows the CSV template and converts the data types to the correct format.
    There are some special cases where the values are not in the template.

    :return: a tuple with the headers and fields for the flights table
    :rtype: tuple(list, list, list)
    """
    flights_heads = ['Date', 'Text', 'Text', 'Text', 'Text', 'hhmm', 'hhmm',
                     'hhmm', 'hhmm', 'hhmm', 'hhmm', 'Decimal', 'Decimal',
                     'Decimal', 'Decimal', 'Decimal', 'Decimal', 'Decimal',
                     'Number', 'Decimal', 'Number', 'Number', 'Number',
                     'Number', 'Number', 'Decimal', 'Decimal', 'Decimal',
                     'Decimal', 'Decimal', 'Decimal', 'Number',
                     'Packed Detail', 'Packed Detail', 'Packed Detail',
                     'Packed Detail', 'Packed Detail', 'Packed Detail',
                     'Decimal', 'Decimal', 'Decimal', 'Decimal', 'Text',
                     'Text', 'Packed Detail', 'Packed Detail', 'Packed Detail',
                     'Packed Detail', 'Packed Detail', 'Packed Detail',
                     'Boolean', 'Boolean', 'Boolean', 'Boolean', 'Boolean',
                     'Text', 'Decimal', 'Decimal']
    flights_fields = [
        'Date', 'AircraftID', 'From', 'To', 'Route', 'TimeOut', 'TimeOff',
        'TimeOn', 'TimeIn', 'OnDuty', 'OffDuty', 'TotalTime', 'PIC',
        'SIC', 'Night', 'Solo', 'CrossCountry', 'NVG', 'NVGOps', 'Distance',
        'DayTakeoffs', 'DayLandingsFullStop', 'NightTakeoffs',
        'NightLandingsFullStop', 'AllLandings', 'ActualInstrument',
        'SimulatedInstrument', 'HobbsStart', 'HobbsEnd', 'TachStart',
        'TachEnd', 'Holds', 'Approach1', 'Approach2', 'Approach3',
        'Approach4', 'Approach5', 'Approach6', 'DualGiven',
        'DualReceived', 'SimulatedFlight', 'GroundTraining',
        'InstructorName', 'InstructorComments', 'Person1', 'Person2',
        'Person3', 'Person4', 'Person5', 'Person6', 'FlightReview',
        'Checkride', 'IPC', 'NVGProficiency', 'FAA6158',
        '[Text]CustomFieldName', '[Numeric]CustomFieldName',
        '[Hours]CustomFieldName'
    ]

    flights_mapping = dict(zip(flights_fields, flights_fields))
    flights_mapping['Date'] = 'DateUTC'
    flights_mapping['AircraftID'] = 'AircraftCode'
    # Not sure since TO and FROM are airport abbreviation not code
    flights_mapping['From'] = 'DepCode'
    flights_mapping['To'] = 'ArrCode'

    flights_mapping['TimeOut'] = 'ArrTimeUTC'
    flights_mapping['TimeOff'] = 'DepTimeUTC'
    flights_mapping['TimeOn'] = 'LdgTimeUTC'
    flights_mapping['TimeIn'] = 'ArrTimeUTC'
    flights_mapping['OnDuty'] = 'DepOffset'
    flights_mapping['OffDuty'] = 'ArrOffset'
    flights_mapping['PIC'] = 'minPIC'
    flights_mapping['SIC'] = 'minCOP'
    flights_mapping['Night'] = 'minNIGHT'
    flights_mapping['Solo'] = 'minSFR'
    flights_mapping['CrossCountry'] = 'minXC'
    flights_mapping['NVGOps'] = 'minAIR'
    flights_mapping['NightLandingsFullStop'] = 'LdgNight'
    flights_mapping['HobbsStart'] = 'HobbsIn'
    flights_mapping['HobbsEnd'] = 'HobbsOut'
    flights_mapping['Holds'] = 'Holding'
    flights_mapping['GroundTraining'] = 'Training'

    # Map flight fields from the meta-data
    fields_flights_data = []
    for data in flight_data:
        flight = {}
        for i, (key, field) in enumerate(flights_mapping.items()):
            value = convert_types(data.meta.get(field, ''), flights_heads[i])
            flight[key] = value

        # Override the AircraftID checking in an aircraft list already created
        flight['AircraftID'] = find_aircraft(aircraft_codes, flight['AircraftID'])
        fields_flights_data.append(flight)

    return flights_heads, fields_flights_data

def prepare_logbook_data_to_csv(aircraft_queryset: None, flight_queryset: None):
    """
    Prepare the data for export to a CSV file.

    Returns a tuple with the headers and fields for both the aircraft and flight tables.
    Follows the CSV template and converts the data types to the correct format.
    There are some special cases where the values are not in the template.

    :return: a tuple with the headers and fields for both the aircraft and flight tables
    :rtype: tuple(list, list, list, list, list, list)
    """
    aircraft_data = aircraft_queryset
    if not aircraft_queryset:
        aircraft_data = DynamicTable.objects.filter(table='Aircraft')

    flight_data = flight_queryset
    if not flight_queryset:
        flight_data = DynamicTable.objects.filter(table='Flight')


    aircraft_heads, fields_aircraft_data, aircraft_codes = prepare_aircraft_data_to_csv(aircraft_data)
    flights_heads, fields_flights_data = prepare_flights_data_to_csv(flight_data, aircraft_codes)

    return (aircraft_heads,
            fields_aircraft_data,

            flights_heads,
            fields_flights_data)


def generate_csv_file(aircraft_heads, fields_aircraft_data,
                      flights_heads, fields_flights_data,
                      file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        # Write the fixed sections
        writer.writerow(['ForeFlight Logbook Import'] + [""] * 57)
        writer.writerow([""] * 58)
        writer.writerow(['Aircraft Table'] + [""] * 57)
        writer.writerow([""] * 58)
        writer.writerow(aircraft_heads)
        writer.writerow(fields_aircraft_data[0].keys())
        for aircraft_data in fields_aircraft_data:
            writer.writerow(aircraft_data.values())

        writer.writerow([""] * 58)
        writer.writerow(['Flights Table'])
        writer.writerow(flights_heads)
        writer.writerow(fields_flights_data[0].keys())
        for flight_data in fields_flights_data:
            writer.writerow(flight_data.values())


    logger.info(f"CSV export complete: {file_path}")