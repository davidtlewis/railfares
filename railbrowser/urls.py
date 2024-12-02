from django.urls import path
from .views import *

urlpatterns = [
    
    path('', welcome_view, name='welcome'),  # Default view
    path('find_fares/', find_fares_view6, name='find_fares6'),
    path('clusters/<str:cluster_id>/', cluster_details_view, name='cluster_details'),
    path("cluster/search/", cluster_search_view, name="cluster_search"),
    path('station/search/', station_search_view, name='station_search'),
    path('stations/<str:nlc_code>/', station_details_view, name='station_details'),
    path('flow/<str:flow_id>/', flow_detail_view, name='flow_details'),
    path('flows/search/', flow_search_view, name='flow_search'),
    path('station-groups/search/', station_group_search_view, name='station_group_search'),
    path('station-groups/<str:group_id>/', station_group_detail_view, name='station_group_details'),
     path('route/search/', route_search_view, name='route_search'),
     path('station/autocomplete/', station_autocomplete, name='station_autocomplete'),
]