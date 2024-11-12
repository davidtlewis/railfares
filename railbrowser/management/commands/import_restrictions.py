import os
import datetime
from django.core.management.base import BaseCommand
from railbrowser.models import Restriction, RestrictionDateBand, TimeRestriction, TrainRestriction

class Command(BaseCommand):
    help = "Imports restrictions data from flat files into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help="The path to the flat file containing restrictions data",
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File {file_path} does not exist."))
            return

        self.stdout.write(self.style.SUCCESS(f"Starting restrictions import from {file_path}..."))

        # Open the file and read each line
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                if line.startswith("/"):  # Skip comments
                    continue

                try:
                    record_type = line[1:3].strip()  # Assume the first character defines the type of restriction record
                    if record_type == 'R':  # Primary restriction record
                        self._import_restriction(line)
                    elif record_type == 'RD':  # Date band record
                        self._import_date_band(line)
                    elif record_type == 'T':  # Time restriction record
                        self._import_time_restriction(line)
                    elif record_type == 'X':  # Train restriction record
                        self._import_train_restriction(line)
                    else:
                        self.stdout.write(self.style.WARNING(f"Unknown record type '{record_type}' on line {line_number}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error parsing line {line_number}: {e}"))

        self.stdout.write(self.style.SUCCESS("Restrictions data import completed successfully."))

    def _import_restriction(self, line):
        """Parses and saves a Restriction record"""
        # Assuming line structure is:
        # R | restriction_code (2 chars) | description (60 chars)
        restriction_code = line[1:3].strip()
        description = line[3:63].strip()

        # Create or update the Restriction
        restriction, created = Restriction.objects.update_or_create(
            restriction_code=restriction_code,
            defaults={'description': description}
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Restriction {restriction_code}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated Restriction {restriction_code}"))

    def _import_date_band(self, line):
        """Parses and saves a RestrictionDateBand record"""
        # Assuming line structure is:
        # D | restriction_code (2 chars) | start_date (8 chars, ddmmyyyy) | end_date (8 chars, ddmmyyyy)
        restriction_code = line[1:3].strip()
        start_date = self._parse_date(line[3:11].strip())
        end_date = self._parse_date(line[11:19].strip())

        try:
            restriction = Restriction.objects.get(restriction_code=restriction_code)
            date_band, created = RestrictionDateBand.objects.update_or_create(
                restriction=restriction,
                start_date=start_date,
                end_date=end_date
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Date Band for Restriction {restriction_code}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated Date Band for Restriction {restriction_code}"))

        except Restriction.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Restriction {restriction_code} not found. Skipping date band record."))

    def _import_time_restriction(self, line):
        """Parses and saves a TimeRestriction record"""
        # Assuming line structure is:
        # T | restriction_code (2 chars) | time_code (10 chars) | start_time (4 chars, hhmm) | end_time (4 chars, hhmm) | days_of_week (7 chars)
        restriction_code = line[1:3].strip()
        time_code = line[3:13].strip()
        start_time = self._parse_time(line[13:17].strip())
        end_time = self._parse_time(line[17:21].strip())
        days_of_week = line[21:28].strip()  # e.g., "MTWTFSS" for Monday to Sunday

        try:
            restriction = Restriction.objects.get(restriction_code=restriction_code)
            time_restriction, created = TimeRestriction.objects.update_or_create(
                restriction=restriction,
                time_code=time_code,
                defaults={
                    'start_time': start_time,
                    'end_time': end_time,
                    'days_of_week': days_of_week
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Time Restriction for {restriction_code}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated Time Restriction for {restriction_code}"))

        except Restriction.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Restriction {restriction_code} not found. Skipping time restriction record."))

    def _import_train_restriction(self, line):
        """Parses and saves a TrainRestriction record"""
        # Assuming line structure is:
        # X | restriction_code (2 chars) | train_id (10 chars) | allowed_classes (3 chars) | quota_controlled (1 char) | weekend_first (1 char)
        restriction_code = line[1:3].strip()
        train_id = line[3:13].strip()
        allowed_classes = line[13:16].strip()
        quota_controlled = line[16:17].strip() == 'Y'
        weekend_first = line[17:18].strip() == 'Y'

        try:
            restriction = Restriction.objects.get(restriction_code=restriction_code)
            train_restriction, created = TrainRestriction.objects.update_or_create(
                restriction=restriction,
                train_id=train_id,
                defaults={
                    'allowed_classes': allowed_classes,
                    'quota_controlled': quota_controlled,
                    'weekend_first': weekend_first
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Train Restriction for {restriction_code}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated Train Restriction for {restriction_code}"))

        except Restriction.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Restriction {restriction_code} not found. Skipping train restriction record."))

    def _parse_date(self, date_str):
        """Parses date from ddmmyyyy format to datetime.date or None"""
        if date_str == '00000000' or not date_str.strip():  # Use '00000000' or empty for null dates
            return None
        try:
            return datetime.datetime.strptime(date_str, "%d%m%Y").date()
        except ValueError:
            return None

    def _parse_time(self, time_str):
        """Parses time from hhmm format to datetime.time or None"""
        if not time_str.strip():
            return None
        try:
            return datetime.datetime.strptime(time_str, "%H%M").time()
        except ValueError:
            return None
