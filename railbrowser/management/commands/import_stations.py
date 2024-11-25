import os
from django.core.management.base import BaseCommand
from railbrowser.models import Station, StationGroup

class Command(BaseCommand):
    help = "Imports stationsonly  from a flat file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Path to the file containing station and group data")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File {file_path} does not exist."))
            return

        self.stdout.write(self.style.SUCCESS(f"Starting import from {file_path}..."))

        stations_to_create = []
        rships = []

        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                if line.startswith("/"):  # Skip comments
                    continue
                
                try:
                    record_type = line[1:2].strip()
                    if record_type == 'L':  # Station record
                        if int(line[13:17]) > 2024: #skip records that are out of date soon
                            station = self._parse_station(line)
                            if station:
                                stations_to_create.append(station)

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error parsing line {line_number}: {e}"))

        print(f'about to bulk create stations numbering {len(stations_to_create)}')
        # Bulk create stations
        Station.objects.bulk_create(stations_to_create, ignore_conflicts=True)

        

        self.stdout.write(self.style.SUCCESS("Import completed successfully."))

    def _parse_station(self, line):
        """Parse an L record to create a Station."""
        uic_code = line[2:9] #uic code
        nlc_code = line[36:40] #nlc code
        name = line[128:143]
        crs_code = line[56:59]
        pte_code = line[77:79]

        return Station(nlc_code=nlc_code, name=name, uic_code=uic_code, crs_code=crs_code, pte_code=pte_code)

    