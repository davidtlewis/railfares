from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Fare, Flow, Station, StationCluster, StationGroup
from .forms import FindFaresForm, ClusterSearchForm, StationSearchForm, FlowSearchForm, StationGroupSearchForm
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.models import Prefetch
from django.db import connection

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
            print(f'lenth of flows: {len(flows)}')
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


def find_fares_view4(request):
    form = FindFaresForm(request.GET or None)
    fares_with_resolved_flows = []  # Initialize results

    if form.is_valid():
        origin_code = form.cleaned_data['origin']
        destination_code = form.cleaned_data['destination']

        try:
            # Get the origin and destination stations
            origin_station = Station.objects.get(nlc_code=origin_code)
            destination_station = Station.objects.get(nlc_code=destination_code)

            # Get associated clusters and groups
            origin_clusters = StationCluster.objects.filter(stations=origin_station)
            destination_clusters = StationCluster.objects.filter(stations=destination_station)

            origin_groups = StationGroup.objects.filter(stations=origin_station)
            destination_groups = StationGroup.objects.filter(stations=destination_station)

            # Get ContentTypes for Station, StationCluster, and StationGroup
            station_type = ContentType.objects.get_for_model(Station)
            cluster_type = ContentType.objects.get_for_model(StationCluster)
            group_type = ContentType.objects.get_for_model(StationGroup)

            # Combine IDs for origin and destination
            origin_ids = (
                [origin_station.id]
                + list(origin_clusters.values_list('id', flat=True))
                + list(origin_groups.values_list('id', flat=True))
            )
            destination_ids = (
                [destination_station.id]
                + list(destination_clusters.values_list('id', flat=True))
                + list(destination_groups.values_list('id', flat=True))
            )

            # Query relevant flows
            flows = Flow.objects.filter(
                Q(origin_content_type=station_type, origin_object_id=origin_station.id) |
                Q(origin_content_type=cluster_type, origin_object_id__in=origin_clusters.values_list('id', flat=True)) |
                Q(origin_content_type=group_type, origin_object_id__in=origin_groups.values_list('id', flat=True)),
                Q(destination_content_type=station_type, destination_object_id=destination_station.id) |
                Q(destination_content_type=cluster_type, destination_object_id__in=destination_clusters.values_list('id', flat=True)) |
                Q(destination_content_type=group_type, destination_object_id__in=destination_groups.values_list('id', flat=True)),
            )

            # Query fares for these flows
            fares = Fare.objects.filter(flow__in=flows).select_related('flow', 'ticket_type')

            # Add resolved origin and destination for each fare
            for fare in fares:
                flow = fare.flow
                fares_with_resolved_flows.append({
                    'fare': fare,
                    'origin': _resolve_generic(flow.origin_content_type, flow.origin_object_id),
                    'destination': _resolve_generic(flow.destination_content_type, flow.destination_object_id),
                })

        except Station.DoesNotExist:
            form.add_error(None, "One or both station codes are invalid.")

    return render(request, 'find_fares.html', {
        'form': form,
        'fares': fares_with_resolved_flows,  # Pass as `fares` for template compatibility
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

def station_group_search_view(request):
    form = StationGroupSearchForm(request.GET or None)
    groups = []  # Initialize groups as an empty list

    if form.is_valid():
        search_query = form.cleaned_data.get("search_query", "").strip()
        if search_query:
            # Search by group_id or name (case-insensitive)
            groups = StationGroup.objects.filter(
                Q(group_id__icontains=search_query) | Q(name__icontains=search_query)
            )

    return render(request, "station_group_search.html", {
        "form": form,
        "groups": groups,
    })

def flow_search_view(request):
    
    if request.method == 'POST':
        form = FlowSearchForm(request.POST)
        if form.is_valid():
            flow_id = form.cleaned_data['flow_id']
            return redirect('flow_detail', flow_id=flow_id)
    else:
        form = FlowSearchForm()
    
    return render(request, 'flow_search.html', {'form': form})

def station_group_detail_view(request, group_id):
    # Get the station group or return a 404 if not found
    group = get_object_or_404(StationGroup, group_id=group_id)

    # Retrieve all stations in the group
    stations = group.stations.all()

    return render(request, "station_group_detail.html", {
        "group": group,
        "stations": stations,
    })