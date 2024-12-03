from django.core.management.base import BaseCommand
from railbrowser.models import Fare, Restriction

# TODO ignore empty restriction codes!
class Command(BaseCommand):
    help = 'Update fare.restriction  to point to the correct restriction object based on the route_code field'

    def handle(self, *args, **kwargs):
        fares  = Fare.objects.all()
        for fare in fares:
            try:
                if fare.restriction_code != '':
                    restriction = Restriction.objects.get(restriction_code=fare.restriction_code)
                    fare.restriction = restriction
                    fare.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully updated Flow {fare.id} with Route {fare.restriction_code}'))
            except Restriction.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Restriction with code {fare.restriction_code} does not exist for fare {fare.id}'))