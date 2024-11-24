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

