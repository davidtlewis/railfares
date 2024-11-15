from django.shortcuts import render
from django.http import JsonResponse
from .models import Fare, Flow, Station, StationCluster
from .forms import FindFaresForm
from django.contrib.contenttypes.models import ContentType

def find_fares(request):
    # Extract the origin and destination from query parameters
    origin_code = request.GET.get('origin')
    destination_code = request.GET.get('destination')

    if not origin_code or not destination_code:
        return JsonResponse({'error': 'Please provide both origin and destination codes'}, status=400)

    try:
        # Query the database for fares from origin to destination
        fares = Fare.objects.filter(
            flow__origin_content_type__model='station',  # Ensure it's a station
            flow__origin_object_id__in=Station.objects.filter(nlc_code=origin_code).values_list('id', flat=True),
            flow__destination_content_type__model='station',  # Ensure it's a station
            flow__destination_object_id__in=Station.objects.filter(nlc_code=destination_code).values_list('id', flat=True)
        ).select_related('flow', 'ticket_type')

        # Serialize the data into a list of dictionaries
        fare_data = [
            {
                'ticket_type': fare.ticket_type.description,
                'fare': fare.fare / 100,  # Convert fare from pence to currency units
                'restriction': fare.restriction_code,
            }
            for fare in fares
        ]

        return JsonResponse({'fares': fare_data})

    except Station.DoesNotExist:
        return JsonResponse({'error': 'One or both station codes are invalid'}, status=404)



def find_fares_view_v1(request):
    form = FindFaresForm(request.GET or None)  # Bind GET data to the form

    fares = None  # Initialize fares to None
    if form.is_valid():  # Validate form submission
        origin_code = form.cleaned_data['origin']
        destination_code = form.cleaned_data['destination']

        try:
            # Query the database for fares from origin to destination
            fares = Fare.objects.filter(
                flow__origin_content_type__model='station',  # Ensure it's a station
                flow__origin_object_id__in=Station.objects.filter(nlc_code=origin_code).values_list('id', flat=True),
                flow__destination_content_type__model='station',  # Ensure it's a station
                flow__destination_object_id__in=Station.objects.filter(nlc_code=destination_code).values_list('id', flat=True)
            ).select_related('flow', 'ticket_type')

        except Station.DoesNotExist:
            form.add_error(None, "One or both station codes are invalid.")

    return render(request, 'find_fares.html', {'form': form, 'fares': fares})

def find_fares_view(request):
    form = FindFaresForm(request.GET or None)
    fares = None  # Initialize fares to None

    if form.is_valid():  # Validate form submission
        origin_code = form.cleaned_data['origin']
        destination_code = form.cleaned_data['destination']

        try:
            # Fetch origin and destination stations
            origin_station = Station.objects.get(nlc_code=origin_code)
            destination_station = Station.objects.get(nlc_code=destination_code)

            # Get clusters containing the origin and destination stations
            origin_clusters = StationCluster.objects.filter(stations=origin_station)
            destination_clusters = StationCluster.objects.filter(stations=destination_station)

            # Get ContentType for Station and StationCluster models
            station_type = ContentType.objects.get_for_model(Station)
            cluster_type = ContentType.objects.get_for_model(StationCluster)

            # Combine ContentType and object_id for both stations and clusters
            origin_criteria = [
                {'content_type': station_type, 'object_id': origin_station.id}
            ] + [
                {'content_type': cluster_type, 'object_id': cluster.id}
                for cluster in origin_clusters
            ]

            destination_criteria = [
                {'content_type': station_type, 'object_id': destination_station.id}
            ] + [
                {'content_type': cluster_type, 'object_id': cluster.id}
                for cluster in destination_clusters
            ]

            # Query for fares matching the combined criteria
            fares = Fare.objects.filter(
                flow__origin_content_type__in=[c['content_type'] for c in origin_criteria],
                flow__origin_object_id__in=[c['object_id'] for c in origin_criteria],
                flow__destination_content_type__in=[c['content_type'] for c in destination_criteria],
                flow__destination_object_id__in=[c['object_id'] for c in destination_criteria],
            ).select_related('flow', 'ticket_type')

        except Station.DoesNotExist:
            form.add_error(None, "One or both station codes are invalid.")

    return render(request, 'find_fares.html', {'form': form, 'fares': fares})
