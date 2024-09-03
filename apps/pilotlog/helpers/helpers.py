import json
from pilotlog.models.dynamic_model import DynamicModel


def load_data(file_path) -> json:
    with open(file_path, 'r') as f:
        # Load as string
        data = f.read()
        f.close()

        # Remove double quotes
        json_data = data.replace('\\"', '"')

        # Parse the corrected JSON string
        data = json.loads(json_data)

        return data


def import_data(file_path):
    data = load_data(file_path)
    total = len(data)

    imported, failed = 0, 0
    errors = []
    for d in data:
        try:
            DynamicModel.objects.get_or_create(**d)
            imported += 1
            # calculate percentage of imported records, show 10% progress
            if imported % (total // 10) == 0:
                print(f"Imported {imported}/{total} records.")
        except Exception as e:
            failed += 1
            print(e)
            errors.append(e)
    print(f"Imported {imported} records. Failed to import {failed} records.")
    print()

    print(errors)
