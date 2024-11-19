from django.urls import path
from .views import *

urlpatterns = [
    path('find_fares_json/', find_fares, name='find_fares_json'),
    path('find_fares2/', find_fares_view2, name='find_fares2'),
    path('clusters/<str:cluster_id>/', cluster_details_view, name='cluster_details'),
    path("cluster/search/", cluster_search_view, name="cluster_search"),
    path('station/search/', station_search_view, name='station_search'),
    path('stations/<str:nlc_code>/', station_details_view, name='station_details'),

]