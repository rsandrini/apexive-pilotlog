import os
import json
import time
import csv
import logging
from pilotlog.models.dynamic_table import DynamicTable
from django_bulk_load import bulk_insert_models
from apexive.settings import BULK_INSERT_CHUNK_SIZE
'''
    Import and Export ForeFlight and Logbook
    Based on ForeFlight: https://cloudfront.foreflight.com/docs/ff/16.2/ForeFlight%20Logbook.pdf
    following the official template and JSON format exported from ForeFlight
'''

logger = logging.getLogger(__name__)


def load_data(file_path) -> json:
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
    data = load_data(file_path)

    objs = [DynamicTable(**d) for d in data]
    logger.info(f"Importing {len(objs)} objects")
    batch_size = BULK_INSERT_CHUNK_SIZE
    for start  in range(0, len(objs), batch_size):
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

def export_data(file_path):
    (aircraft_heads, aircraft_fields, fields_aircraft_data,
     flights_heads, flights_fields, fields_flights_data ) = prepare_logbook_data()

    generate_csv_file(aircraft_heads,
                      aircraft_fields,
                      fields_aircraft_data,

                      flights_heads,
                      flights_fields,
                      fields_flights_data,
                      file_path)

def prepare_logbook_data():

    aircraft_data = DynamicTable.objects.filter(table='Aircraft')
    flight_data = DynamicTable.objects.filter(table='Flight')

    aircraft_heads = ['Text', 'Text', 'Text', 'YYYY', 'Text', 'Text', 'Text',
                      'Text', 'Text', 'Text', 'Boolean', 'Boolean',
                      'Boolean', 'Boolean']
    aircraft_fields = ['AircraftID', 'EquipmentType', 'TypeCode', 'Year',
                       'Make', 'Model', 'Category', 'Class', 'GearType',
                       'EngineType', 'Complex', 'HighPerformance',
                       'Pressurized', 'TAA']

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
                     '[Text]CustomFieldName', '[Numeric]CustomFieldName',
                     '[Hours]CustomFieldName', '[Counter]CustomFieldName',
                     '[Date]CustomFieldName', '[DateTime]CustomFieldName',
                     '[Toggle]CustomFieldName', 'PilotComments']
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
        '[Hours]CustomFieldName', '[Counter]CustomFieldName',
        '[Date]CustomFieldName', '[DateTime]CustomFieldName',
        '[Toggle]CustomFieldName', 'PilotComments'
    ]

    fields_aircraft_data = []
    for data in aircraft_data:
        aircraft = []
        for field in aircraft_fields:
            aircraft.append(data.meta.get(field, ''))
        fields_aircraft_data.append(aircraft)

    fields_flights_data = []
    for data in flight_data:
        flights = []
        for field in flights_fields:
            flights.append(data.meta.get(field, ''))
        fields_flights_data.append(flights)


    print(fields_aircraft_data)

    return (aircraft_heads,
            aircraft_fields,
            fields_aircraft_data,

            flights_heads,
            flights_fields,
            fields_flights_data)


def generate_csv_file(aircraft_heads, aircraft_fields, fields_aircraft_data,
                      flights_heads, flights_fields, fields_flights_data,
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
        writer.writerow(aircraft_fields)
        for aircraft_data in fields_aircraft_data:
            writer.writerow(aircraft_data)

        writer.writerow([""] * 58)
        writer.writerow(['Flights Table'])
        writer.writerow(flights_heads)
        writer.writerow(flights_fields)
        for flight_data in fields_flights_data:
            writer.writerow(flight_data)


    logger.info(f"CSV export complete: {file_path}")