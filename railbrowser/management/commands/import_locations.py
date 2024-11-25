import os
from django.core.management.base import BaseCommand
from railbrowser.models import Station, StationGroup

class Command(BaseCommand):
    help = "Imports stations, groups, and memberships from a flat file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Path to the file containing station and group data")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File {file_path} does not exist."))
            return

        self.stdout.write(self.style.SUCCESS(f"Starting import from {file_path}..."))

        stations_to_create = []
        groups_to_create = []
        memberships = []

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
                    elif record_type == 'G':  # Group record
                        if int(line[12:17]) > 2024: #skip records that are out of date soon
                            group = self._parse_group(line)
                            if group:
                                groups_to_create.append(group)
                    elif record_type == 'M':  # Membership record
                        if int(line[12:17]) > 2024: #skip records that are out of date soon
                            membership = self._parse_membership(line)
                            if membership:
                                memberships.append(membership)

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error parsing line {line_number}: {e}"))

        print(f'about to bulk create stations numbering {len(stations_to_create)}')
        # Bulk create stations
        Station.objects.bulk_create(stations_to_create, ignore_conflicts=True)

        print(f'about to bulk create station groups numbering {len(groups_to_create)}')
        # Bulk create station groups
        StationGroup.objects.bulk_create(groups_to_create, ignore_conflicts=True)

        # Establish memberships
        self._create_memberships(memberships)

        self.stdout.write(self.style.SUCCESS("Import completed successfully."))

    def _parse_station(self, line):
        """Parse an L record to create a Station."""
        uic_code = line[2:9] #uic code
        nlc_code = line[36:40] #nlc code
        name = line[128:143]
        crs_code = line[56:59]
        pte_code = line[77:79]

        return Station(nlc_code=nlc_code, name=name, uic_code=uic_code, crs_code=crs_code, pte_code=pte_code)

    def _parse_group(self, line):
        """Parse a G record to create a StationGroup."""
        group_id = line[2:9].strip()
        nlc_code = group_id[2:6]
        name = line[33:49].strip()
        return StationGroup(group_id=group_id, name=name, nlc_code=nlc_code)

    def _parse_membership(self, line):
        """Parse an M record to create a membership relationship."""
        group_id = line[2:9]
        member_uic = line[17:24]
        member_crs = line[24:27]
        return (group_id, member_uic, member_crs)

    def _create_memberships(self, memberships):
        """Create relationships between StationGroup and Station."""
        memberships_by_group = {}
        for group_id, member_uic, member_crs in memberships:
            if group_id not in memberships_by_group:
                memberships_by_group[group_id] = []
            memberships_by_group[group_id].append(member_uic)

        for group_id, member_uics in memberships_by_group.items():
            try:
                group = StationGroup.objects.get(group_id=group_id)
                stations = Station.objects.filter(uic_code__in=member_uics)
                group.stations.add(*stations)
            except StationGroup.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Group {group_id} does not exist. Skipping..."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating memberships for group {group_id}: {e}"))
