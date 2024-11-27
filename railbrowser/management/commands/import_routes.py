import os
from django.core.management.base import BaseCommand
from railbrowser.models import Route

class Command(BaseCommand):
    help = "Imports strouts only  from a flat file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Path to the file containing route data")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File {file_path} does not exist."))
            return

        self.stdout.write(self.style.SUCCESS(f"Starting import from {file_path}..."))

        routes_to_create = []

        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                if line.startswith("/"):  # Skip comments
                    continue
                
                try:
                    record_type = line[1:2].strip()
                    if record_type == 'R':  # route record
                        if int(line[11:15]) > 2024: #process only current  records 
                            route = self._parse_route(line)
                            if route:
                                routes_to_create.append(route)

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error parsing line {line_number}: {e}"))

        print(f'about to bulk create routes numbering {len(routes_to_create)}')
        # Bulk create routes
        Route.objects.bulk_create(routes_to_create, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("Import completed successfully."))

    def _parse_route(self, line):
        route_code = line[2:7] 
        description = line[31:47] #nlc code
        atb_desc_1 = line[47:82]
        atb_desc_2 = line[82:117]
        atb_desc_3 = line[117:152]
        atb_desc_4 = line[152:187]
        cc_desc = line[187:203]

        return Route(route_code=route_code, description=description, atb_desc_1=atb_desc_1, atb_desc_2=atb_desc_2, atb_desc_3=atb_desc_3, atb_desc_4=atb_desc_4, cc_desc=cc_desc)
    

    