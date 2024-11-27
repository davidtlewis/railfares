from django.core.management.base import BaseCommand
from railbrowser.models import Flow, Route

class Command(BaseCommand):
    help = 'Update flow.route to point to the correct Route object based on the route_code field'

    def handle(self, *args, **kwargs):
        flows = Flow.objects.all()
        for flow in flows:
            try:
                route = Route.objects.get(route_code=flow.route_code)
                flow.route = route
                flow.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully updated Flow {flow.id} with Route {route.route_code}'))
            except Route.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Route with code {flow.route_code} does not exist for Flow {flow.id}'))