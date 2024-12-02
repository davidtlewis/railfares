import os
import datetime
from django.core.management.base import BaseCommand
from railbrowser.models import Restriction, TimeRestrictionDateBand, TimeRestriction, TrainRestriction, Station

class Command(BaseCommand):
    help = "Imports restrictions data from flat files into the database"
    # all a bit knackers as the sub rsstrictions are suposed to be lined to the retriction header by a _combination_ of cf_mkr AND restriction code
    # but I don't undersatnd how it all fits together yet

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
                    record_type = line[1:3].strip()  
                    # if record_type == 'RH':  # Primary restriction record
                    #     self._import_restriction(line)
                    
                    # elif record_type == 'TR':  # Time restriction record
                    #     self._import_time_restriction(line)

                    if record_type == 'TD':  # Time restriction Date band record # need to do this AFTER the TR records
                        self._import_time_restriction_date_band(line)

                    # elif record_type == 'X':  # Train restriction record
                    #     self._import_train_restriction(line)
                    # else:
                    #     self.stdout.write(self.style.WARNING(f"Unknown record type '{record_type}' on line {line_number}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error parsing line {line_number}: {e} Line {line}"))

        self.stdout.write(self.style.SUCCESS("Restrictions data import completed successfully."))

    def _import_restriction(self, line):
        """Parses and saves a Restriction record"""
        # Assuming line structure is:
        # R | restriction_code (2 chars) | description (60 chars)
        cf_mkr = line[3:4]
        restriction_code = line[4:6]
        description = line[6:36]
        description_out = line[36:86]
        description_rtn= line[86:136]
        type_out = line[136:137]
        type_in = line[137:138]
        change_ind = line[138:139]

        # Create or update the Restriction
        restriction, created = Restriction.objects.update_or_create(
            restriction_code=restriction_code,
            cf_mkr = cf_mkr,
            defaults={
                'description': description,
                'description_out': description_out,
                'description_rtn': description_rtn,
                'type_out': type_out,
                'type_in': type_in,
                'change_ind': change_ind,
                }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Restriction {restriction_code}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated Restriction {restriction_code}"))

    def _import_time_restriction_date_band(self, line):
        """Parses and saves a TimeRestrictionDateBand record"""
        cf_mkr = line[3:4]
        restriction_code = line[4:6]
        sequence_no = line[6:10]
        out_ret = line[10:11]
        date_from = line[11:15] #need to fix to get right year !
        date_to = line[15:19] #need to fix to get right year !
        days_of_week = line[19:26]
        
        try:
            time_restriction = TimeRestriction.objects.get(restriction__restriction_code=restriction_code, cf_mkr=cf_mkr, sequence_no=sequence_no) #now thinking the relationship should be the other way round.  as there are lots of locations in each time recrod code.
            # TODO check out BRfares again

            time_date_band, created = TimeRestrictionDateBand.objects.update_or_create(
                time_restriction=time_restriction,
                out_ret = out_ret,
                date_from=self._parse_short_date(date_from),
                date_to=self._parse_short_date(date_to),
                defaults={
                    'days_of_week': days_of_week,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Date Band for Restriction {restriction_code}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated Date Band for Restriction {restriction_code}"))

        except Restriction.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Restriction {restriction_code} not found. Skipping date band record."))

    def _import_time_restriction(self, line):
        """Parses and saves a TimeRestriction record"""
        cf_mkr = line[3:4]
        restriction_code = line[4:6]
        sequence_no = line[6:10]
        out_ret = line[10:11]
        time_from = line[11:15]
        time_to = line[15:19]
        arr_dep_via = line[19:20]
        location = line[20:23] #crs code !

        try:
            restriction = Restriction.objects.get(restriction_code=restriction_code)
            if location != "   ":
                station= Station.objects.get(crs_code=location)
            else:
                station = None 
            time_restriction, created = TimeRestriction.objects.update_or_create(
                restriction=restriction,
                sequence_no = sequence_no,
                out_ret = out_ret,
                cf_mkr = cf_mkr,
                defaults={
                    'time_from': self._parse_time(time_from),
                    'time_to': self._parse_time(time_to),
                    'arr_dep_via': arr_dep_via,
                    'location': station
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

    def _parse_short_date(self, date_str):
        """Parses date from MMDD format to datetime.date or None"""
        if date_str == '00000000' or not date_str.strip():  # Use '00000000' or empty for null dates
            return None
        try:
            return datetime.datetime.strptime(date_str, "%m%d").date()  #TODO need to interpret these in terms of the headline date bands in records "RD – Restriction Dates record"
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
