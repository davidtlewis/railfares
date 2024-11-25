import os
import datetime
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from railbrowser.models import Flow, Station, StationGroup, StationCluster, Restriction, Fare

class Command(BaseCommand):
    help = "Imports  cluster data from flat files into the database"

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
                if line.startswith("/"):  # Skip comments
                    continue

                if int(line[13:17]) > 2024: #only deal with current cluser data
                    c_code = line[1:5]
                    s_id = line[5:9] #might be a station of a stationgroup
                    # print(f'line number: {line_number}.  c_code {c_code} and s_id {s_id}')

                    cluster, created = StationCluster.objects.get_or_create(cluster_id = c_code)
                    # print(f'cluster: {cluster} created: {created}')

                          
                    try:
                        station = Station.objects.get(nlc_code=s_id)
                        cluster.stations.add(station)
                        # print(f'Line: {line_number}.  station: {station} added to cluster: {cluster}')
                    except Station.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Station {s_id} does not exist. "))

                    try:    
                        stationGroup = StationGroup.objects.get(nlc_code=s_id)
                        cluster.station_groups.add(stationGroup)
                        # print(f'LIne: {line_number}.  Station Group: {stationGroup} added to cluster: {cluster}')
                    except StationGroup.DoesNotExist:
                        pass
                    #     self.stdout.write(self.style.WARNING(f"Group {s_id} does not exist. Skipping..."))
                    # except Exception as e:
                    #     self.stdout.write(self.style.ERROR(f"Error adding station group to cluster for group {s_id}: {e}"))

                  