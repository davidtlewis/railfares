import os
import datetime
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from railbrowser.models import Flow, Station, StationCluster, Restriction, Fare

class Command(BaseCommand):
    help = "Imports station, from flat files into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help="The path to the flat file containing cluster  data",
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File {file_path} does not exist."))
            return
        self.stdout.write(self.style.SUCCESS(f"Starting import from {file_path}..."))

        # Open the file and read each line
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                print(f'line number {line_number}')
                if line.startswith("/"):  # Skip comments
                    continue

                record_type = line[1:2]
                if record_type == 'L':
                    end_year = int(line[13:17])
                    if end_year > 2024:
                        print(line)
                        s_nlc = line[36:40] #nlc code
                        s_description = line[128:143]
                        station, created = Station.objects.update_or_create(nlc_code = s_nlc, defaults={"name": s_description})
                        # station.save()
                        print(f'created {station}  station')
                        print