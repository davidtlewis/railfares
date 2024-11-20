from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Fare, Flow, Station, StationCluster
from .forms import FindFaresForm, ClusterSearchForm, StationSearchForm, FlowSearchForm
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.models import Prefetch
from django.db import connection



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
    origin_station = None
    destination_station = None
    origin_clusters = None
    destination_clusters= None

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

    return render(request, 'find_fares.html', {
        'form': form,
        'fares': fares,
        'origin_station': origin_station,
        'destination_station': destination_station,
        'origin_clusters': origin_clusters,
        'destination_clusters': destination_clusters,

        })


def find_fares_view2(request):
    form = FindFaresForm(request.GET or None)
    fares_with_resolved_flows = None  # Initialize variable to hold fares with origin/destination details

    origin_station = None
    origin_clusters = []
    destination_station = None
    destination_clusters = []

    if form.is_valid():  # Validate form submission
        origin_code = form.cleaned_data['origin']
        destination_code = form.cleaned_data['destination']

        try:
            # Fetch origin and destination stations
            origin_station = Station.objects.get(nlc_code=origin_code)
            destination_station = Station.objects.get(nlc_code=destination_code)

            # Get clusters containing the origin and destination stations
            # origin_clusters = StationCluster.objects.filter(stations=origin_station)
            origin_clusters = StationCluster.objects.filter(stations__id=origin_station.id)
            destination_clusters = StationCluster.objects.filter(stations__id=destination_station.id)

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

            # Add resolved origin and destination to each fare
            fares_with_resolved_flows = []
            for fare in fares:
                flow = fare.flow
                fares_with_resolved_flows.append({
                    'fare': fare,
                    'flow': flow,
                    'origin': _resolve_generic(flow.origin_content_type, flow.origin_object_id),
                    'destination': _resolve_generic(flow.destination_content_type, flow.destination_object_id),
                })

        except Station.DoesNotExist:
            form.add_error(None, "One or both station codes are invalid.")

    return render(request, 'find_fares2.html', {
        'form': form,
        'fares_with_resolved_flows': fares_with_resolved_flows,
        'origin_station': origin_station,
        'origin_clusters': origin_clusters,
        'destination_station': destination_station,
        'destination_clusters': destination_clusters,
    })


def find_fares_view3(request):
    form = FindFaresForm(request.GET or None)
    fares_with_resolved_flows = []  # Initialize variable to hold fares with origin/destination details

    if form.is_valid():
        origin_code = form.cleaned_data['origin']
        destination_code = form.cleaned_data['destination']
        print(f"Origin Code: {origin_code}, Destination Code: {destination_code}")

        try:
            # Fetch origin and destination stations
            origin_station = Station.objects.get(nlc_code=origin_code)
            destination_station = Station.objects.get(nlc_code=destination_code)

            # Fetch clusters containing the origin and destination stations
            origin_clusters = StationCluster.objects.filter(stations=origin_station)
            destination_clusters = StationCluster.objects.filter(stations=destination_station)

            # Get ContentType for Station and StationCluster models
            station_type = ContentType.objects.get_for_model(Station)
            cluster_type = ContentType.objects.get_for_model(StationCluster)

            # Restrict the query to include only valid origin and destination pairs
            cluster_origin_ids = list(origin_clusters.values_list('id', flat=True))
            cluster_destination_ids = list(destination_clusters.values_list('id', flat=True))

            print(f"Cluster Origin IDs: {cluster_origin_ids}") 
            print(f"Cluster Destination IDs: {cluster_destination_ids}") 

            # Query for flows matching the combined criteria
            flows = Flow.objects.filter(
                Q(origin_content_type=station_type, origin_object_id=origin_station.id) |
                Q(origin_content_type=cluster_type, origin_object_id__in=cluster_origin_ids),
                Q(destination_content_type=station_type, destination_object_id=destination_station.id) |
                Q(destination_content_type=cluster_type, destination_object_id__in=cluster_destination_ids)
            )

            # Debug: Print flows retrieved
            print(f'Flows: {list(flows.values_list("id", flat=True))}')

            # Query fares for these flows
            fares = Fare.objects.filter(flow__in=flows).select_related('flow', 'ticket_type')

            # Add resolved origin and destination to each fare
            for fare in fares:
                flow = fare.flow
                fares_with_resolved_flows.append({
                    'fare': fare,
                    'origin': _resolve_generic(flow.origin_content_type, flow.origin_object_id),
                    'destination': _resolve_generic(flow.destination_content_type, flow.destination_object_id),
                })

            print(f'Length of fares: {len(fares)}') 
            print(f'Length of fares_with_resolved_flows: {len(fares_with_resolved_flows)}')

        except Station.DoesNotExist:
            form.add_error(None, "One or both station codes are invalid.")

    return render(request, 'find_fares3.html', {
        'form': form,
        'fares_with_resolved_flows': fares_with_resolved_flows,
    })

def _resolve_generic(content_type, object_id):
    """Resolve a GenericForeignKey to its object"""
    if content_type and object_id:
        return content_type.get_object_for_this_type(id=object_id)
    return None

def cluster_details_view(request, cluster_id):
    # Get the cluster or return a 404 if not found
    cluster = get_object_or_404(StationCluster, cluster_id=cluster_id)

    # Retrieve all stations in the cluster
    stations = cluster.stations.all()

    return render(request, "cluster_details.html", {
        "cluster": cluster,
        "stations": stations,
    })

def cluster_search_view(request):
    form = ClusterSearchForm(request.GET or None)
    clusters = []

    if form.is_valid():
        search_query = form.cleaned_data.get("search_query", "").strip()
        if search_query:
            # Search by cluster_id or name (case-insensitive)
            clusters = StationCluster.objects.filter(
                Q(cluster_id__icontains=search_query) 
            )

    return render(request, "cluster_search.html", {
        "form": form,
        "clusters": clusters,
    })

def station_details_view(request, nlc_code):
    # Get the station or return a 404 if not found
    station = get_object_or_404(Station, nlc_code=nlc_code)

    # Get the clusters the station belongs to
    clusters = station.clusters.all()  # Assuming a `related_name="clusters"` on the ManyToManyField

    return render(request, "station_details.html", {
        "station": station,
        "clusters": clusters,
    })

def station_search_view(request):
    form = StationSearchForm(request.GET or None)
    stations = []  # Initialize stations as an empty list

    if form.is_valid():
        search_query = form.cleaned_data.get("search_query", "").strip()
        if search_query:
            # Search by nlc_code or name (case-insensitive)
            stations = Station.objects.filter(
                Q(nlc_code__icontains=search_query) | Q(name__icontains=search_query)
            )

    return render(request, "station_search.html", {
        "form": form,
        "stations": stations,
    })

def flow_detail_view(request, flow_id):
    flow = get_object_or_404(Flow, flow_id=flow_id)
    return render(request, 'flow_detail.html', {'flow': flow})

def flow_search_view(request):
    if request.method == 'POST':
        form = FlowSearchForm(request.POST)
        if form.is_valid():
            flow_id = form.cleaned_data['flow_id']
            return redirect('flow_detail', flow_id=flow_id)
    else:
        form = FlowSearchForm()
    
    return render(request, 'flow_search.html', {'form': form})