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

