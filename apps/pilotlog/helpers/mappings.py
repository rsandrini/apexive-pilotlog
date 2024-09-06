def get_aircraft_mapping() -> (list, list):
    """
    Returns the mapping between the aircraft heads and the column names in the
    PilotLog database.

    Returns:
        tuple: a tuple containing two elements:
            1. a list of strings, which are the headers for the aircraft CSV file
            2. a dictionary mapping each aircraft head to the column name in the
               PilotLog database
    """
    aircraft_heads = ['Text', 'Text', 'Text', 'YYYY', 'Text', 'Text', 'Text',
                      'Text', 'Text', 'Text', 'Boolean', 'Boolean',
                      'Boolean', 'Boolean']
    aircraft_mapping = {
        'AircraftID': 'RefSearch',
        'EquipmentType': 'EquipmentType',
        'TypeCode': 'TypeCode',
        'Year': 'Record_Modified',
        'Make': 'Make',
        'Model': 'Model',
        'Category': 'Category',
        'Class': 'Class',
        'GearType': 'Tailwheel',
        'EngineType': 'Power',
        'Complex': 'Complex',
        'HighPerformance': 'HighPerf',
        'Pressurized': 'Kg5700',
        'TAA': 'Aerobatic'
    }
    assert len(aircraft_heads) == len(aircraft_mapping)
    return aircraft_heads, aircraft_mapping

def get_flights_mapping():
    """
    Returns the mapping between the flight heads and the column names in the
    PilotLog database.
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

    flight_mapping = {
        'Date': 'DateUTC',
        'AircraftID': 'AircraftCode',
        'From': 'DepCode',
        'To': 'ArrCode',
        'Route': 'Route',
        'TimeOut': 'ArrTimeUTC',
        'TimeOff': 'DepTimeUTC',
        'TimeOn': 'LdgTimeUTC',
        'TimeIn': 'ArrTimeUTC',
        'OnDuty': 'DepOffset',
        'OffDuty': 'ArrOffset',
        'TotalTime': 'TotalTime',
        'PIC': 'minPIC',
        'SIC': 'minCOP',
        'Night': 'minNIGHT',
        'Solo': 'minSFR',
        'CrossCountry': 'minXC',
        'NVG': 'NVG',
        'NVGOps': 'minAIR',
        'Distance': 'Distance',
        'DayTakeoffs':'DayTakeoffs',
        'DayLandingsFullStop':'DayLandingsFullStop',
        'NightTakeoffs':'NightTakeoffs',
        'NightLandingsFullStop': 'LdgNight',
        'AllLandings':'AllLandings',
        'ActualInstrument': 'ActualInstrument',
        'SimulatedInstrument': 'SimulatedInstrument',
        'HobbsStart': 'HobbsIn',
        'HobbsEnd': 'HobbsOut',
        'TachStart': 'TachStart',
        'TachEnd': 'TachEnd',
        'Holds': 'Holding',
        'Approach1': 'Approach1',
        'Approach2': 'Approach2',
        'Approach3': 'Approach3',
        'Approach4': 'Approach4',
        'Approach5': 'Approach5',
        'Approach6': 'Approach6',
        'DualGiven': 'DualGiven',
        'DualReceived': 'DualReceived',
        'SimulatedFlight': 'SimulatedFlight',
        'GroundTraining': 'Training',
        'InstructorName': 'InstructorName',
        'InstructorComments': 'InstructorComments',
        'Person1': 'Person1',
        'Person2': 'Person2',
        'Person3': 'Person3',
        'Person4': 'Person4',
        'Person5': 'Person5',
        'Person6': 'Person6',
        'FlightReview': 'FlightReview',
        'Checkride': 'Checkride',
        'IPC': 'IPC',
        'NVGProficiency': 'NVGProficiency',
        'FAA6158': 'FAA6158',
        '[Text]CustomFieldName': '[Text]CustomFieldName',
        '[Numeric]CustomFieldName': '[Numeric]CustomFieldName',
        '[Hours]CustomFieldName': '[Hours]CustomFieldName'
    }
    assert len(flights_heads) == len(flight_mapping)
    return flights_heads, flight_mapping