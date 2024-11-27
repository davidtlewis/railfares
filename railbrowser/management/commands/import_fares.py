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

        fares_to_create =[]
        batch_counter = 0

        # Open the file and read each line
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                if line.startswith("/"):  # Skip comments
                    continue

                # Parse each line according to the fixed-width fields defined
                try:
                    record_type = line[1:2].strip()
                    if record_type == 'T':
                        fare = self._parse_fare_record(line)
                        if fare:
                            fares_to_create.append(fare)
                            batch_counter = batch_counter + 1
                            if batch_counter >= 5000:
                                Fare.objects.bulk_create(fares_to_create)
                                self.stdout.write(
                                    self.style.SUCCESS(f"Line {line_number}: Imported {len(fares_to_create)} new flares records.")
                                )
                                batch_counter = 0
                                fares_to_create.clear()
                            # print(f'Line numner: {line_number}  Batch numcounter {batch_counter}')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error parsing line {line_number}: {e}"))
                # print(f'line {line_number}')
            if fares_to_create:
                Fare.objects.bulk_create(fares_to_create)
                self.stdout.write(
                    self.style.SUCCESS(f"Imported {len(fares_to_create)} new flow records.")
                )
        self.stdout.write(self.style.SUCCESS("Data import completed successfully."))

    def _parse_fare_record(self, line):
        """Parses Fare record """
        fare =  int(line[12:20].strip())  # Fare in pence
        restriction_code = line[20:22].strip()
        #get the restriction object
        restriction = self._get_or_create_restriction(restriction_code)


        # Find the Flow and ticket_type record that this Fare belongs to
        flow_id = line[2:9].strip()
        ticket_code = line[9:12].strip()
        flow = Flow.objects.get(flow_id__exact=flow_id)
        ticket_type = TicketType.objects.get(ticket_code__exact=ticket_code)
        fare_data = {
            'flow':flow,
            'ticket_type':ticket_type,
            'fare':fare,
            'restriction_code':restriction_code,
            'restriction':restriction
        }

        return Fare(**fare_data)
    
        # fare, created = Fare.objects.update_or_create(
        #     flow=flow,
        #     ticket_type=ticket_type,
        #     fare=fare,
        #     restriction_code=restriction_code
        # )
        # self.stdout.write(self.style.SUCCESS(f"Created Fare record for Flow ID {flow_id} with Ticket Code {ticket_code}"))
        # if created:
            #     self.stdout.write(self.style.SUCCESS(f"Created Fare record for Flow ID {flow_id} with Ticket Code {ticket_code}"))
            # else:
            #     self.stdout.write(self.style.SUCCESS(f"Updated Fare record for Flow ID {flow_id} with Ticket Code {ticket_code}"))

        # except Flow.DoesNotExist:
        #     self.stdout.write(self.style.ERROR(f"Flow ID {flow_id} not found. Skipping fare record."))
        # except TicketType.DoesNotExist:
        #     self.stdout.write(self.style.ERROR(f"TicketType with code {ticket_code} not found. Skipping fare record."))
        
        
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
