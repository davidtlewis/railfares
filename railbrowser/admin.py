from django.contrib import admin
from railbrowser.models import *


class  StationAdmin(admin.ModelAdmin):
    list_display = ('nlc_code','name')
    search_fields = ["nlc_code","name"]


class FlowAdmin(admin.ModelAdmin):
    list_display = ('flow_id','origin','destination')
    search_fields = ["nlc_code",'origin ','destination']

class StationClusterAdmin(admin.ModelAdmin):
    search_fields = ["cluster_id"]

class FareAdmin(admin.ModelAdmin):
    list_display = ('flow','ticket_type','fare','restriction_code')

class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('id','ticket_code','class_of_travel','ticket_type')
    search_fields = ['origin ','destination']

admin.site.register(Station, StationAdmin)
admin.site.register(StationCluster, StationClusterAdmin)
admin.site.register(Flow, FlowAdmin)
admin.site.register(Fare, FareAdmin)
admin.site.register(TicketType, TicketTypeAdmin)


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


