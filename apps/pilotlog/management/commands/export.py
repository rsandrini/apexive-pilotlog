from django.core.management.base import BaseCommand, CommandError
from apps.pilotlog.helpers.import_export import export_to_csv


class Command(BaseCommand):
    help = "Exports the aircraft and flight data in CSV format"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to CSV file for export")

    def handle(self, *args, **options):
        self.stdout.write("Exporting data...")
        export_to_csv(options["file"])
        self.stdout.write(f"Done! Check the exported CSV file in "
                          f"{options["file"]}")
