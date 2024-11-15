import os
import datetime
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from railbrowser.models import Flow, Station, StationCluster, Restriction, Fare, TicketType

class Command(BaseCommand):
    help = "Imports fare data from flat files into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help="The path to the flat file containing fare data",
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File {file_path} does not exist."))
            return

        self.stdout.write(self.style.SUCCESS(f"Starting import from {file_path}..."))

        # Get ContentTypes for Station and StationCluster models
        station_type = ContentType.objects.get_for_model(Station)
        cluster_type = ContentType.objects.get_for_model(StationCluster)

        # Open the file and read each line
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                if line.startswith("/"):  # Skip comments
                    continue

                # Parse each line according to the fixed-width fields defined
                try:
                    record_type = line[1:2].strip()
                    if record_type == 'F':
                        self._import_flow_record(line, station_type, cluster_type)
                    elif record_type == 'T':
                        self._import_fare_record(line)
                    else:
                        self.stdout.write(self.style.WARNING(f"Unknown record type '{record_type}' on line {line_number}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error parsing line {line_number}: {e}"))
                print(f'line {line_number}')
        self.stdout.write(self.style.SUCCESS("Data import completed successfully."))

    def _import_flow_record(self, line, station_type, cluster_type):
        """Parses and saves a Flow record with GenericForeignKey for origin and destination"""
        
        # Parse data from fixed-width line
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
        }

        # Determine origin content type and ID
        origin_content_type, origin_object_id = self._get_content_type_and_id(origin_code, station_type, cluster_type)
        flow_data['origin_content_type'] = origin_content_type
        flow_data['origin_object_id'] = origin_object_id

        # Determine destination content type and ID
        destination_content_type, destination_object_id = self._get_content_type_and_id(destination_code, station_type, cluster_type)
        flow_data['destination_content_type'] = destination_content_type
        flow_data['destination_object_id'] = destination_object_id

        # Save Flow record
        flow, created = Flow.objects.update_or_create(
            flow_id=flow_data['flow_id'],
            defaults=flow_data
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Flow record with ID {flow.flow_id}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated Flow record with ID {flow.flow_id}"))

    def _import_fare_record(self, line):
        """Parses and saves a Fare record linked to a Flow"""
        fare_data = {
            # 'update_marker': line[0:1].strip(),
            'fare': int(line[12:20].strip()),  # Fare in pence
            'restriction_code': line[20:22].strip(),
        }

        # Find the Flow and ticket_type record that this Fare belongs to
        flow_id = line[2:9].strip()
        ticket_code = line[9:12].strip()

        try:
            flow = Flow.objects.get(flow_id=flow_id)
            fare_data['flow'] = flow

            # Find the TicketType for this fare
            ticket_type = TicketType.objects.get(ticket_code=ticket_code)
            fare_data['ticket_type'] = ticket_type

            # Save or update Fare record
            fare, created = Fare.objects.update_or_create(
                flow=flow,
                ticket_type=ticket_type,
                defaults=fare_data
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Fare record for Flow ID {flow_id} with Ticket Code {ticket_code}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated Fare record for Flow ID {flow_id} with Ticket Code {ticket_code}"))

        except Flow.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Flow ID {flow_id} not found. Skipping fare record."))
        except TicketType.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"TicketType with code {ticket_code} not found. Skipping fare record."))
        
        fare_data = {
            'ticket_code': line[9:12].strip(),
            'fare': int(line[12:20].strip()),  # Fare in pence
            'restriction_code': line[20:22].strip(),
        }

        # Find the Flow record that this Fare belongs to
        flow_id = line[2:9].strip()
        try:
            flow = Flow.objects.get(flow_id=flow_id)
            fare_data['flow'] = flow

            # Save or update Fare record
            fare, created = Fare.objects.update_or_create(
                flow=flow,
                ticket_type=fare_data['ticket_code'],
                defaults=fare_data
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Fare record for Flow ID {flow_id} with Ticket Code {fare_data['ticket_code']}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated Fare record for Flow ID {flow_id} with Ticket Code {fare_data['ticket_code']}"))

        except Flow.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Flow ID {flow_id} not found. Skipping fare record."))

    def _get_content_type_and_id(self, code, station_type, cluster_type):
        """Determine if code corresponds to a Station or StationCluster and return ContentType and ID"""
        try:
            # Check if code corresponds to a Station
            station = Station.objects.get(nlc_code=code)
            return station_type, station.id
        except Station.DoesNotExist:
            pass
        
        try:
            # Check if code corresponds to a StationCluster
            cluster = StationCluster.objects.get(cluster_id=code)
            return cluster_type, cluster.id
        except StationCluster.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Code {code} not found in Station or StationCluster"))
            return None, None

    def _get_or_create_restriction(self, code):
        """Retrieve or create a Restriction based on the restriction code"""
        if not code:
            return None
        restriction, created = Restriction.objects.get_or_create(
            restriction_code=code,
            defaults={'description': f"Automatically imported restriction {code}"}
        )
        return restriction

    def _parse_date(self, date_str):
        """Parses date from ddmmyyyy format to datetime.date or None"""
        if date_str == '31122999':  # High date indicates no end date
            return None
        try:
            return datetime.datetime.strptime(date_str, "%d%m%Y").date()
        except ValueError:
            return None
