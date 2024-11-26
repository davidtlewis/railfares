import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from railbrowser.models import Flow, Station, StationCluster, StationGroup, Restriction

class Command(BaseCommand):
    help = "Imports flow data from flat files into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help="The path to the flat file containing flow data",
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File {file_path} does not exist."))
            return

        self.stdout.write(self.style.SUCCESS(f"Starting flow import from {file_path}..."))

        # Get ContentTypes for Station, StationGroup and StationCluster models
        station_type = ContentType.objects.get_for_model(Station)
        cluster_type = ContentType.objects.get_for_model(StationCluster)
        group_type = ContentType.objects.get_for_model(StationGroup)

        # Prepare lists for bulk creation and updates
        flows_to_create = []
        unresolved_origins = set()
        unresolved_destinations = set()

        # existing_flows = {f.flow_id: f for f in Flow.objects.all()}
        batch_counter = 0
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                if line.startswith("/"):  # Skip comments
                    continue
                try:
                    record_type = line[1:2].strip()
                    if record_type == 'F':
                        flow = self._parse_flow_record(
                            line, station_type, cluster_type, group_type
                        )
                        if flow:
                            flows_to_create.append(flow)
                            batch_counter = batch_counter + 1
                            if batch_counter >= 4000:
                                Flow.objects.bulk_create(flows_to_create)
                                self.stdout.write(
                                    self.style.SUCCESS(f"Imported {len(flows_to_create)} new flow records.")
                                )
                                batch_counter = 0
                                flows_to_create.clear()

                            print(f'Line numner: {line_number}  Batch numcounter {batch_counter}')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error parsing line {line_number}: {e}"))

                # Perform bulk_create for last few  flows
            if flows_to_create:
                Flow.objects.bulk_create(flows_to_create)
                self.stdout.write(
                    self.style.SUCCESS(f"Imported {len(flows_to_create)} new flow records.")
                )

        self.stdout.write(self.style.SUCCESS("Flow data import completed successfully."))

    def _parse_flow_record(self, line, station_type, cluster_type, group_type):
        """Parses a Flow record and returns a Flow object, or None if the record is not in right timeframe"""
        # Parse data from fixed-width line
        start_date = self._parse_date2(line[28:36])
        end_date = self._parse_date2(line[20:28])
        if start_date > datetime.now().date() and end_date < datetime.now().date():
            return None
        
        origin_code = line[2:6].strip()
        destination_code = line[6:10].strip()

        flow_data = {
            'route_code': line[10:15].strip(),
            'status_code': line[15:18].strip(),
            'usage_code': line[18:19].strip(),
            'direction': line[19:20].strip(),
            'end_date': self._parse_date(line[20:28]),
            'start_date': self._parse_date(line[28:36]),
            'toc_code': line[36:39].strip(),
            'cross_london_indicator': line[39:40].strip(),
            'ns_discount_indicator': line[40:41].strip(),
            'publication_indicator': line[41:42].strip() == 'Y',
            'flow_id': line[42:49].strip(),
            'source_data': line,
            
        }

        # print('origin_code:', origin_code)
        # print('destination_code:', destination_code)
        # print('Flow data:', flow_data)
        # print('about to resolve origin')
        # Resolve origin and destination
        flow_data['origin_content_type'], flow_data['origin_global_id'], flow_data['origin_object'] = self._get_content_type_and_id(
            origin_code, station_type, cluster_type, group_type
        )
        # print('Flow data:', flow_data)
        # print('about to resolve destination')
        flow_data['destination_content_type'], flow_data['destination_global_id'],  flow_data['destination_object'] = self._get_content_type_and_id(
            destination_code, station_type, cluster_type, group_type
        )
        # print('Flow data:', flow_data)
        # Create a new Flow instance
        # print(f'created flow - not yet written')
        return Flow(**flow_data)

    def _get_content_type_and_id(self, code, station_type, cluster_type, group_type):
        """Determine if code corresponds to a Station or Stationgroup or  StationCluster and return ContentType and ID"""
        try:
            # Check if code corresponds to a StationGroup
            stationGroup = StationGroup.objects.get(nlc_code=code)
            return group_type, stationGroup.global_id, stationGroup
        except StationGroup.DoesNotExist:
            pass    
    
        try:
            # Check if code corresponds to a Station
            station = Station.objects.get(nlc_code=code)
            return station_type, station.global_id, station
        except Station.DoesNotExist:
            pass

        try:
            # Check if code corresponds to a StationCluster
            cluster = StationCluster.objects.get(cluster_id=code)
            return cluster_type, cluster.global_id, cluster
        except StationCluster.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Code {code} not found in Station or StationCluster"))
            return None, None

    def _parse_date(self, date_str):
        """Parses date from ddmmyyyy format to datetime.date or None"""
        if date_str == '31122999':  # High date indicates no end date
            return None
        try:
            return datetime.strptime(date_str, "%d%m%Y").date()
        except ValueError:
            return None

    def _parse_date2(self, date_str):
        """Parses date from ddmmyyyy format to datetime.date or None"""
        try:
            return datetime.strptime(date_str, "%d%m%Y").date()
        except ValueError:
            return None
