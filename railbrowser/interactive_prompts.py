destination_station = Station.objects.filter(nlc_code__icontains='6856')[0]
origin_station = Station.objects.filter(nlc_code__icontains='7212')[0]

# Get clusters containing the origin and destination stations
# origin_clusters = StationCluster.objects.filter(stations=origin_station)
origin_clusters = StationCluster.objects.filter(stations__id=origin_station.id)
destination_clusters = StationCluster.objects.filter(stations__id=destination_station.id)

# Get ContentType for Station and StationCluster models
station_type = ContentType.objects.get_for_model(Station)
cluster_type = ContentType.objects.get_for_model(StationCluster)


origin_criteria = [{'content_type': station_type, 'object_id': origin_station.id}]

destination_criteria = [{'content_type': station_type, 'object_id': destination_station.id}]

origin_criteria = [ {'content_type': station_type, 'object_id': origin_station.id} ] + [{'content_type': cluster_type, 'object_id': cluster.id} for cluster in origin_clusters ] 

destination_criteria = [{'content_type': station_type, 'object_id': destination_station.id}] + [{'content_type': cluster_type, 'object_id': cluster.id} for cluster in destination_clusters]


fares = Fare.objects.filter( \
                flow__origin_content_type__in=[c['content_type'] for c in origin_criteria], \
                flow__origin_object_id__in=[c['object_id'] for c in origin_criteria], \
                flow__destination_content_type__in=[c['content_type'] for c in destination_criteria], \
                flow__destination_object_id__in=[c['object_id'] for c in destination_criteria], \
            ).select_related('flow', 'ticket_type')

fares2 = Fare.objects.filter( \
                flow__origin_content_type__in=[c['content_type'] for c in origin_criteria], \
                flow__origin_object_id__in=[c['object_id'] for c in origin_criteria], \
                flow__destination_content_type__in=[c['content_type'] for c in destination_criteria], \
                flow__destination_object_id__in=[c['object_id'] for c in destination_criteria], \
            )


fares = Fare.objects.filter( \
                flow__origin_content_type__in=[c['content_type'] for c in origin_criteria], \
                flow__origin_object_id__in=[c['object_id'] for c in origin_criteria], \
                flow__destination_content_type__in=[c['content_type'] for c in destination_criteria], \
                flow__destination_object_id__in=[c['object_id'] for c in destination_criteria], \
            ).select_related('flow')