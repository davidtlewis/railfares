from django.contrib import admin
from railbrowser.models import *


class StationAdmin(admin.ModelAdmin):
    list_display = ('global_id','nlc_code','name','pte_code','crs_code')
    search_fields = ["nlc_code","name","pte_code",'crs_code']

class StationGroupAdmin(admin.ModelAdmin):
    list_display = ('global_id','nlc_code','name', 'group_id')
    search_fields = ('name', 'group_id')
    filter_horizontal = ('stations',)  # Use a horizontal filter for managing many-to-many relationships

class FlowAdmin(admin.ModelAdmin):
    list_display = ("flow_id",  "origin_object",  "destination_object","route_code","direction","toc_code",)
    search_fields = (
        "flow_id",
    )

    # def origin(self, obj):
    #     """Display the origin object."""
    #     return f"{obj.origin_content_type.model} (ID: {obj.origin_object_id})"

    # def destination(self, obj):
    #     """Display the destination object."""
    #     return f"{obj.destination_content_type.model} (ID: {obj.destination_object_id})"

class StationClusterAdmin(admin.ModelAdmin):
    list_display = ('global_id','cluster_id','station_count', 'station_group_count')
    search_fields = ["cluster_id"]
    raw_id_fields = ('stations','station_groups')  # Use raw_id_fields for foreign keys

    def station_count(self, obj):
        return obj.stations.count()
    station_count.short_description = 'Number of Stations'

    def station_group_count(self, obj):
        return obj.station_groups.count()
    station_group_count.short_description = 'Number of Station Groups'

class FareAdmin(admin.ModelAdmin):
    list_display = ('flow','ticket_type','fare','restriction_code')
    raw_id_fields = ('flow', 'ticket_type')  # Use raw_id_fields for foreign keys

class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('id','ticket_code','description',   'class_of_travel','ticket_type','end_date','start_date')
    search_fields = ['description','ticket_code']

class RestrictionAdmin(admin.ModelAdmin):
    list_display = ('restriction_code','description')
    search_fields = ['restriction_code','description']

class RouteAdmin(admin.ModelAdmin):
    list_display = ('route_code','description')
    search_fields = ['route_code','description']

admin.site.register(Station, StationAdmin)
admin.site.register(StationCluster, StationClusterAdmin)
admin.site.register(Flow, FlowAdmin)
admin.site.register(Fare, FareAdmin)
admin.site.register(TicketType, TicketTypeAdmin)
admin.site.register(StationGroup, StationGroupAdmin)
admin.site.register(Route, RouteAdmin)

# Inline classes for related models
class RestrictionDateBandInline(admin.TabularInline):
    model = RestrictionDateBand
    extra = 1  # Number of empty forms to display in the admin
    fields = ['date_from', 'date_to','days_of_week']  # Fields to display in the inline

class TimeRestrictionDateBandInline(admin.TabularInline):
    model = TimeRestrictionDateBand
    extra = 1  # Number of empty forms to display in the admin
    fields = ['date_from', 'date_to','days_of_week']  # Fields to display in the inline

class TimeRestrictionInline(admin.TabularInline):
    model = TimeRestriction
    extra = 1
    fields = ['sequence_no', 'out_ret', 'time_from', 'time_to', 'arr_dep_via', 'location']
    raw_id_fields = ('location',)  # Use raw_id_fields for foreign keys

class TrainRestrictionInline(admin.TabularInline):
    model = TrainRestriction
    extra = 1
    fields = ['train_id', 'allowed_classes', 'quota_controlled', 'weekend_first']

# Main Restriction admin configuration
@admin.register(Restriction)
class RestrictionAdmin(admin.ModelAdmin):
    list_display = ['restriction_code', 'description','cf_mkr']  # Fields to display in the main list
    search_fields = ['restriction_code', 'description']  # Enable searching by these fields
    inlines = [RestrictionDateBandInline, TimeRestrictionInline,  TrainRestrictionInline]  # Attach inlines

# Registering related models independently (optional)
@admin.register(RestrictionDateBand)
class RestrictionDateBandAdmin(admin.ModelAdmin):
    list_display = ['restriction','cf_mkr', 'date_from', 'date_to', 'days_of_week']  
    search_fields = ['restriction__restriction_code']

@admin.register(TimeRestriction)
class TimeRestrictionAdmin(admin.ModelAdmin):
    list_display = ['restriction', 'sequence_no', 'out_ret', 'time_from', 'time_to', 'arr_dep_via', 'location']
    search_fields = ['restriction__restriction_code', 'location']
    raw_id_fields = ('restriction',)  # Use raw_id_fields for foreign keys

@admin.register(TimeRestrictionDateBand)
class TimeRestrictionDateBandAdmin(admin.ModelAdmin):
    list_display = ['time_restriction', 'date_from', 'date_to', 'days_of_week',  'out_ret']
    search_fields = ['time_restriction__restriction__restriction_code']
    raw_id_fields = ('time_restriction',)  # Use raw_id_fields for foreign keys


@admin.register(TrainRestriction)
class TrainRestrictionAdmin(admin.ModelAdmin):
    list_display = ['restriction', 'train_id', 'allowed_classes', 'quota_controlled', 'weekend_first']
    search_fields = ['restriction__restriction_code', 'train_id']


