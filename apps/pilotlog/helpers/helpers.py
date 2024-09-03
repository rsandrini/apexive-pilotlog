import json
import time
import logging
from pilotlog.models.dynamic_table import DynamicTable
from django_bulk_load import bulk_insert_models
from apexive.settings import BULK_INSERT_CHUNK_SIZE

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
            # Bulk insert using django_bulk_load, faster than bulk_create from django
            bulk_insert_models(
                models=batch,
                ignore_conflicts=True
            )
            logger.info(f"Batch starting at index {start} inserted successfully")
        except Exception as e:
            logger.error(f"Exception in import data at batch starting index {start}: {e}")

    logger.info(f"Imported {len(objs)} objects")