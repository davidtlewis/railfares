from django.contrib import admin
from railbrowser.models import *


class  StationAdmin(admin.ModelAdmin):
    list_display = ('nlc_code','name')
    search_fields = ["nlc_code","name"]

class StationGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_id')
    search_fields = ('name', 'group_id')
    filter_horizontal = ('stations',)  # Use a horizontal filter for managing many-to-many relationships

class FlowAdmin(admin.ModelAdmin):
    list_display = ("id", "origin", "destination")
    search_fields = (
        "id",  # Search by Flow ID
        "origin_content_type__model",  # Search by origin type (Station, Cluster, Group)
        "destination_content_type__model",  # Search by destination type
        "origin_object_id",  # Search by origin ID
        "destination_object_id",  # Search by destination ID
    )

    def origin(self, obj):
        """Display the origin object."""
        return f"{obj.origin_content_type.model} (ID: {obj.origin_object_id})"

    def destination(self, obj):
        """Display the destination object."""
        return f"{obj.destination_content_type.model} (ID: {obj.destination_object_id})"

class StationClusterAdmin(admin.ModelAdmin):
    search_fields = ["cluster_id"]
    raw_id_fields = ('stations',)  # Use raw_id_fields for foreign keys

class FareAdmin(admin.ModelAdmin):
    list_display = ('flow','ticket_type','fare','restriction_code')
    raw_id_fields = ('flow', 'ticket_type')  # Use raw_id_fields for foreign keys

class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('id','ticket_code','description',   'class_of_travel','ticket_type','end_date','start_date')
    search_fields = ['description','ticket_code']

admin.site.register(Station, StationAdmin)
admin.site.register(StationCluster, StationClusterAdmin)
admin.site.register(Flow, FlowAdmin)
admin.site.register(Fare, FareAdmin)
admin.site.register(TicketType, TicketTypeAdmin)
admin.site.register(StationGroup, StationGroupAdmin)


# Inline classes for related models
class RestrictionDateBandInline(admin.TabularInline):
    model = RestrictionDateBand
    extra = 1  # Number of empty forms to display in the admin
    fields = ['start_date', 'end_date']  # Fields to display in the inline

class TimeRestrictionInline(admin.TabularInline):
    model = TimeRestriction
    extra = 1
    fields = ['time_code', 'start_time', 'end_time', 'days_of_week']

class TrainRestrictionInline(admin.TabularInline):
    model = TrainRestriction
    extra = 1
    fields = ['train_id', 'allowed_classes', 'quota_controlled', 'weekend_first']

# Main Restriction admin configuration
@admin.register(Restriction)
class RestrictionAdmin(admin.ModelAdmin):
    list_display = ['restriction_code', 'description']  # Fields to display in the main list
    search_fields = ['restriction_code', 'description']  # Enable searching by these fields
    inlines = [RestrictionDateBandInline, TimeRestrictionInline, TrainRestrictionInline]  # Attach inlines

# Registering related models independently (optional)
@admin.register(RestrictionDateBand)
class RestrictionDateBandAdmin(admin.ModelAdmin):
    list_display = ['restriction', 'start_date', 'end_date']
    search_fields = ['restriction__restriction_code']

@admin.register(TimeRestriction)
class TimeRestrictionAdmin(admin.ModelAdmin):
    list_display = ['restriction', 'time_code', 'start_time', 'end_time', 'days_of_week']
    search_fields = ['restriction__restriction_code', 'time_code']

@admin.register(TrainRestriction)
class TrainRestrictionAdmin(admin.ModelAdmin):
    list_display = ['restriction', 'train_id', 'allowed_classes', 'quota_controlled', 'weekend_first']
    search_fields = ['restriction__restriction_code', 'train_id']


