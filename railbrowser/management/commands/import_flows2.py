from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from railbrowser.models import Flow, Station, StationCluster, StationGroup
import csv

class Command(BaseCommand):
    help = "Import flow records from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Path to the CSV file containing flow data")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        if not file_path:
            self.stdout.write(self.style.ERROR("No file path provided."))
            return

        flows_to_create = []

        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    origin_global_id = self.resolve_global_id(row['origin_type'], row['origin_id'])
                    destination_global_id = self.resolve_global_id(row['destination_type'], row['destination_id'])

                    if origin_global_id and destination_global_id:
                        flows_to_create.append(
                            Flow(
                                origin_content_type=ContentType.objects.get(model=row['origin_type'].lower()),
                                origin_global_id=origin_global_id,
                                destination_content_type=ContentType.objects.get(model=row['destination_type'].lower()),
                                destination_global_id=destination_global_id,
                            )
                        )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing row {row}: {e}"))

        # Bulk create the flows
        Flow.objects.bulk_create(flows_to_create)
        self.stdout.write(self.style.SUCCESS(f"Imported {len(flows_to_create)} flow records."))

    def resolve_global_id(self, object_type, object_id):
        """Resolve the global_id for the given object type and ID."""
        try:
            if object_type.lower() == 'station':
                return Station.objects.get(nlc_code=object_id).global_id
            elif object_type.lower() == 'stationcluster':
                return StationCluster.objects.get(cluster_id=object_id).global_id
            elif object_type.lower() == 'stationgroup':
                return StationGroup.objects.get(nlc_code=object_id).global_id
            else:
                raise ValueError(f"Unknown object type: {object_type}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error resolving {object_type} with ID {object_id}: {e}"))
            return None