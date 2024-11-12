import os
from datetime import datetime
from django.core.management.base import BaseCommand
from railbrowser.models import TicketType

class Command(BaseCommand):
    help = "Imports ticket types data from flat files into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help="The path to the flat file containing ticket types data",
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File {file_path} does not exist."))
            return

        self.stdout.write(self.style.SUCCESS(f"Starting ticket type import from {file_path}..."))

        # Open the file and read each line
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                if line.startswith("/"):  # Skip comments
                    continue

                ticket_type_data = {
                    'ticket_code': line[1:4].strip(),
                    'description': line[28:43].strip(),
                    'class_of_travel': line[43:44].strip(),
                    'ticket_type': line[44:45].strip(),
                    'max_passengers': int(line[54:57].strip()),
                    'min_passengers': int(line[57:60].strip()),
                    'max_adults': int(line[60:63].strip()),
                    'min_adults': int(line[63:66].strip()),
                    'max_children': int(line[66:69].strip()),
                    'min_children': int(line[69:72].strip()),
                    'start_date': self._parse_date(line[12:20].strip()),
                    'end_date': self._parse_date(line[4:12].strip()),
                    # there are more fields TODO
                }

                # Save or update TicketType record
                ticket_type, created = TicketType.objects.update_or_create(
                    ticket_code=ticket_type_data['ticket_code'],
                    defaults=ticket_type_data
                )
            self.stdout.write(self.style.SUCCESS("Ticket types data import completed successfully."))



    def _parse_date(self, date_str):
        """Parses date from ddmmyyyy format to datetime.date or None"""
        if date_str == '00000000' or not date_str.strip():
            return None
        try:
            return datetime.strptime(date_str, "%d%m%Y").date()
        except ValueError:
            return None
