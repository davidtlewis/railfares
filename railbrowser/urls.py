from django.urls import path
from .views import *

urlpatterns = [
    
    path('find_fares4/', find_fares_view4, name='find_fares4'),
    path('find_fares5/', find_fares_view5, name='find_fares5'),
    path('clusters/<str:cluster_id>/', cluster_details_view, name='cluster_details'),
    path("cluster/search/", cluster_search_view, name="cluster_search"),
    path('station/search/', station_search_view, name='station_search'),
    path('stations/<str:nlc_code>/', station_details_view, name='station_details'),
    path('flow/<str:flow_id>/', flow_detail_view, name='flow_details'),
    path('flows/search/', flow_search_view, name='flow_search'),
    path('station-groups/search/', station_group_search_view, name='station_group_search'),
    path('station-groups/<str:group_id>/', station_group_detail_view, name='station_group_details'),

]