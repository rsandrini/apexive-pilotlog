from django.core.management.base import BaseCommand, CommandError
from apps.pilotlog.helpers.import_export import import_data


class Command(BaseCommand):
    help = "Import JSON files into the database"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="JSON file for importing")

    def handle(self, *args, **options):
        self.stdout.write("Starting import data")
        import_data(options["file"])

        self.stdout.write("Finished import data")
