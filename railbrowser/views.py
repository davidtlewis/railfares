from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Fare, Flow, Station, StationCluster, StationGroup
from .forms import FindFaresForm, ClusterSearchForm, StationSearchForm, FlowSearchForm, StationGroupSearchForm
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.models import Prefetch
from django.db import connection

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
            #TODO Probably need to make the clusters include groups as well.  This will invlove change in model and the elect query above


            origin_groups = StationGroup.objects.filter(stations=origin_station)
            destination_groups = StationGroup.objects.filter(stations=destination_station)

            print(f'Origin Clusters: {list(origin_clusters.values_list("id", flat=True))}')
            print(f'Destination Clusters: {list(destination_clusters.values_list("id", flat=True))}')
            print(f'Origin Groups: {list(origin_groups.values_list("id", flat=True))}')
            print(f'Destination Groups: {list(destination_groups.values_list("id", flat=True))}')

            
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

             # Debug: Print flows retrieved
            print(f'Flows: {list(flows.values_list("id", flat=True))}')
            print(f'lenth of flows: {len(flows)}')

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
            print(f'Length of fares: {len(fares)}') 
            print(f'Length of fares_with_resolved_flows: {len(fares_with_resolved_flows)}')


            for item in fares_with_resolved_flows:
                print(f"Origin: {item['origin']}, Destination: {item['destination']}")

        except Station.DoesNotExist:
            form.add_error(None, "One or both station codes are invalid.")

    return render(request, 'find_fares4.html', {
        'form': form,
        'fares': fares_with_resolved_flows,  # Pass as `fares` for template compatibility
    })

def find_fares_view5(request):
    form = FindFaresForm(request.GET or None)
    fares_with_resolved_flows = []

    if form.is_valid():
        origin_code = form.cleaned_data['origin']
        destination_code = form.cleaned_data['destination']

        try:
            origin_station = Station.objects.get(nlc_code=origin_code)
            destination_station = Station.objects.get(nlc_code=destination_code)

            origin_groups = StationGroup.objects.filter(stations=origin_station)
            destination_groups = StationGroup.objects.filter(stations=destination_station)

            origin_clusters = StationCluster.objects.filter(stations=origin_station)
            destination_clusters = StationCluster.objects.filter(stations=destination_station)

            origin_groups = StationGroup.objects.filter(stations=origin_station)
            destination_groups = StationGroup.objects.filter(stations=destination_station)

            station_type = ContentType.objects.get_for_model(Station)
            cluster_type = ContentType.objects.get_for_model(StationCluster)
            group_type = ContentType.objects.get_for_model(StationGroup)

            # origin_ids = [origin_station.id] + list(origin_clusters.values_list('id', flat=True)) + list(origin_groups.values_list('id', flat=True))
            # destination_ids = [destination_station.id] + list(destination_clusters.values_list('id', flat=True)) + list(destination_groups.values_list('id', flat=True))

            origin_ids = [origin_station.id] + list(origin_clusters.values_list('id', flat=True)) + list(origin_groups.values_list('id', flat=True))
            destination_ids = [destination_station.id] + list(destination_clusters.values_list('id', flat=True)) + list(destination_groups.values_list('id', flat=True))


            #debug print
            print(f'Origin Station: {origin_station}')
            print(f'Destination Station: {destination_station}')
            print(f'Origin Groups: {origin_groups}')
            print(f'Desctination Groups: {destination_groups}')
            
            print(f'Origin Clusters: {list(origin_clusters.values_list("id", flat=True))}')
            print(f'Destination Clusters: {list(destination_clusters.values_list("id", flat=True))}')
            print(f'Origin Groups: {list(origin_groups.values_list("id", flat=True))}')
            print(f'Destination Groups: {list(destination_groups.values_list("id", flat=True))}')
            print(f'Origin IDs: {origin_ids}')
            print(f'Destination IDs: {destination_ids}')

            #this is plain wrong !
            flows = Flow.objects.filter(
                Q(origin_content_type=station_type, origin_object_id__in=origin_ids),
                Q(destination_content_type=station_type, destination_object_id__in=destination_ids),
            )

            print(f'Flows: {list(flows.values_list("id", flat=True))}')

            fares = Fare.objects.filter(flow__in=flows).select_related('flow', 'ticket_type')

            for fare in fares:
                flow = fare.flow
                origin = _resolve_generic(flow.origin_content_type, flow.origin_object_id)
                destination = _resolve_generic(flow.destination_content_type, flow.destination_object_id)

                # Add type info to each object
                origin_type = type(origin).__name__ if origin else None
                destination_type = type(destination).__name__ if destination else None

                fares_with_resolved_flows.append({
                    'fare': fare,
                    'origin': origin,
                    'origin_type': origin_type,
                    'destination': destination,
                    'destination_type': destination_type,
                })

        except Station.DoesNotExist:
            form.add_error(None, "One or both station codes are invalid.")

    return render(request, 'find_fares5.html', {
        'form': form,
        'fares': fares_with_resolved_flows,
    })


def find_fares_view6(request):
    form = FindFaresForm(request.GET or None)
    fares_with_resolved_flows = []
    flows = []
    origin_station = None
    destination_station = None


    if form.is_valid():
        origin_code = form.cleaned_data['origin']
        destination_code = form.cleaned_data['destination']
        origin_station = None
        destination_station = None

        try:
            # todo  - extend clusters to those including the station group as well as the station itself
            origin_station = Station.objects.get(nlc_code=origin_code)
            destination_station = Station.objects.get(nlc_code=destination_code)

            origin_global_ids = [origin_station.global_id] + list(
                StationGroup.objects.filter(stations=origin_station).values_list('global_id', flat=True)
            ) + list(
                StationCluster.objects.filter(stations=origin_station).values_list('global_id', flat=True)
            )

            destination_global_ids = [destination_station.global_id] + list(
                StationCluster.objects.filter(stations=destination_station).values_list('global_id', flat=True)
            ) + list(
                StationGroup.objects.filter(stations=destination_station).values_list('global_id', flat=True)
            )

            flows = Flow.objects.filter(
                Q(origin_global_id__in=origin_global_ids) &
                Q(destination_global_id__in=destination_global_ids)
            )

            #debug print
            # print(f'Origin Station: {origin_station}')
            # print(f'Destination Station: {destination_station}')
            # print(f'Origin IDs: {origin_global_ids}')
            # print(f'Destination IDs: {destination_global_ids}')
            print(f'Flows: {list(flows.values_list("id", flat=True))}')

            fares = Fare.objects.filter(flow__in=flows).select_related('flow', 'ticket_type')

            for fare in fares:
                flow = fare.flow
                origin = _resolve_generic(flow.origin_content_type, flow.origin_object_id)
                destination = _resolve_generic(flow.destination_content_type, flow.destination_object_id)
                # Add type info to each object
                origin_type = type(origin).__name__ if origin else None
                destination_type = type(destination).__name__ if destination else None

                fares_with_resolved_flows.append({
                    'fare': fare,
                    'origin': origin,
                    'origin_type': origin_type,
                    'destination': destination,
                    'destination_type': destination_type,
                    'flow': flow,
                })

        except Station.DoesNotExist:
            form.add_error(None, "One or both station codes are invalid.")

    return render(request, 'find_fares6.html', {
        'form': form,
        'fares': fares_with_resolved_flows,
        'flows': flows,
        'origin_station': origin_station,
        'destination_station': destination_station,
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

    # Retrieve all stationGroupss in the cluster
    stations = cluster.stations.all()
    station_groups = cluster.station_groups.all()

    return render(request, "cluster_details.html", {
        "cluster": cluster,
        "stations": stations,
        "station_groups": station_groups,
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

    groups = StationGroup.objects.filter(stations=station)

    # Get the clusters the station belongs to
    clusters = station.clusters.all()  # Assuming a `related_name="clusters"` on the ManyToManyField

    cluster_of_groups = StationCluster.objects.filter(station_groups__in=groups)

    return render(request, "station_details.html", {
        "station": station,
        "groups": groups,
        "clusters": clusters,
        "cluster_of_groups": cluster_of_groups,
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

def station_group_search_view(request):
    form = StationGroupSearchForm(request.GET or None)
    groups = []  # Initialize groups as an empty list

    if form.is_valid():
        search_query = form.cleaned_data.get("search_query", "").strip()
        if search_query:
            # Search by group_id or name (case-insensitive)
            groups = StationGroup.objects.filter(
                Q(group_id__icontains=search_query) | Q(name__icontains=search_query) | Q(nlc_code__icontains=search_query)
            )

    return render(request, "station_group_search.html", {
        "form": form,
        "groups": groups,
    })


def station_group_detail_view(request, group_id):
    # Get the station group or return a 404 if not found
    group = get_object_or_404(StationGroup, group_id=group_id)

    # Retrieve all stations in the group
    stations = group.stations.all()

    return render(request, "station_group_detail.html", {
        "group": group,
        "stations": stations,
    })


def flow_search_view(request):
    form = FlowSearchForm(request.GET or None)
    flows = []  # Initialize as empty

    if form.is_valid():
        flow_id = form.cleaned_data.get("flow_id")
        origin_query = form.cleaned_data.get("origin")
        destination_query = form.cleaned_data.get("destination")

        # Start with an empty query
        query = Q()

        if flow_id:
            query &= Q(id=flow_id)

        if origin_query:
            query &= Q(
                Q(origin_global_id__in=Station.objects.filter(
                    Q(name__icontains=origin_query) | Q(nlc_code__icontains=origin_query)
                ).values_list("global_id", flat=True)) |
                Q(origin_global_id__in=StationCluster.objects.filter(
                    Q(cluster_id__icontains=origin_query)  # Fixed: Search by cluster_id instead of name
                ).values_list("global_id", flat=True)) |
                Q(origin_global_id__in=StationGroup.objects.filter(
                    Q(name__icontains=origin_query) | Q(group_id__icontains=origin_query)
                ).values_list("global_id", flat=True))
            )

        if destination_query:
            query &= Q(
                Q(destination_global_id__in=Station.objects.filter(
                    Q(name__icontains=destination_query) | Q(nlc_code__icontains=destination_query)
                ).values_list("global_id", flat=True)) |
                Q(destination_global_id__in=StationCluster.objects.filter(
                    Q(cluster_id__icontains=destination_query)  # Fixed: Search by cluster_id instead of name
                ).values_list("global_id", flat=True)) |
                Q(destination_global_id__in=StationGroup.objects.filter(
                    Q(name__icontains=destination_query) | Q(group_id__icontains=destination_query)
                ).values_list("global_id", flat=True))
            )

        flows = Flow.objects.filter(query).select_related("origin_content_type", "destination_content_type")

    return render(request, "flow_search.html", {
        "form": form,
        "flows": flows,
    })


def flow_detail_view(request, flow_id):
    # Retrieve the flow or raise 404 if not found
    flow = get_object_or_404(Flow.objects.select_related("origin_content_type", "destination_content_type"), id=flow_id)

    # Retrieve fares associated with this flow
    fares = Fare.objects.filter(flow=flow).select_related("ticket_type")

    return render(request, "flow_detail.html", {
        "flow": flow,
        "fares": fares,
    })

def welcome_view(request):
    return render(request, 'welcome.html')