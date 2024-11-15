from django.urls import path
from .views import find_fares, find_fares_view

urlpatterns = [
    path('find_fares_json/', find_fares, name='find_fares_json'),
    path('find_fares/', find_fares_view, name='find_fares'),


]