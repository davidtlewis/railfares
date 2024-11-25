from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
import uuid

class TicketType(models.Model):
    update_marker = models.CharField(max_length=1)
    ticket_code = models.CharField(max_length=3, unique=True)
    description = models.CharField(max_length=100)
    class_of_travel = models.CharField(max_length=1, choices=[('1', 'First'), ('2', 'Standard'), ('9', 'Undefined')])
    ticket_type = models.CharField(max_length=1, choices=[('S', 'Single'), ('R', 'Return'), ('N', 'Season')])
    max_passengers = models.PositiveIntegerField()
    min_passengers = models.PositiveIntegerField()
    max_adults = models.PositiveIntegerField()
    min_adults = models.PositiveIntegerField()
    max_children = models.PositiveIntegerField()
    min_children = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Ticket Type {self.ticket_code}"

class Flow(models.Model):
    # Generic Foreign Key setup for Origin
    origin_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="origin_flows", null=True)
    origin_global_id = models.UUIDField(null=True)  # Globally unique origin ID
    origin_object = GenericForeignKey('origin_content_type', 'origin_global_id')  # Generic foreign key for origin
    
    # Generic Foreign Key setup for Destination
    destination_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="destination_flows", null=True)
    destination_global_id = models.UUIDField(null=True)  # Globally unique destination ID
    destination_object = GenericForeignKey('destination_content_type', 'destination_global_id')

    route_code = models.CharField(max_length=5)
    status_code = models.CharField(max_length=3, default='000')
    usage_code = models.CharField(max_length=1)
    direction = models.CharField(max_length=1)
    end_date = models.DateField(null=True, blank=True)
    start_date = models.DateField()
    toc_code = models.CharField(max_length=3)
    cross_london_indicator = models.CharField(max_length=1)
    ns_discount_indicator = models.CharField(max_length=1)
    publication_indicator = models.BooleanField(default=False)
    flow_id = models.CharField(max_length=7, unique=True)
    source_data = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"Flow from {self.origin_object} to {self.destination_object}"

class Fare(models.Model):
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE, related_name="fares")
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name="fares")
    # ticket_code = models.CharField(max_length=3)
    fare = models.PositiveIntegerField(help_text="Fare in pence")  # Store fare in pence to avoid floating-point issues
    restriction_code = models.CharField(max_length=2, null=True, blank=True)
    # Foreign key to Restriction, if defined
    # restriction_code = models.ForeignKey(
    #     'Restriction',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='flows'
    # )

    def __str__(self):
        return f"Fare for Flow ID {self.flow.flow_id}"

class Station(models.Model):
    nlc_code = models.CharField(max_length=4, unique=True)
    uic_code = models.CharField(max_length=7, unique=True)
    name = models.CharField(max_length=100)
    crs_code = models.CharField(max_length=3, null=True)
    pte_code = models.CharField(max_length=2, null=True)
    global_id = models.UUIDField(default=uuid.uuid4, unique=True)  # Globally unique ID

    def __str__(self):
        return f"Station {self.name} ({self.nlc_code})"

class StationGroup(models.Model):
    group_id = models.CharField(max_length=7, unique=True)  # Unique identifier for the group
    name = models.CharField(max_length=100, blank=True, null=True)  # Descriptive name for the group
    nlc_code = models.CharField(max_length=4, unique=True, null=True, blank=True)  # Derived NLC code
    stations = models.ManyToManyField('Station', related_name="station_groups")  # Many-to-many relationship
    global_id = models.UUIDField(default=uuid.uuid4, unique=True)  # Globally unique ID
    shadow_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="real_group",null=True, blank=True) #  just to keep a link tothe annoying fake station of same nnc


    def save(self, *args, **kwargs):
        # Automatically derive the NLC code from the UIC if not provided
        if not self.nlc_code:
            self.nlc_code = self.group_id[2:6]  # Characters 3 to 6 (0-indexed)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"StationGroup {self.nlc_code} ({self.group_id})"

class StationCluster(models.Model):
    cluster_id = models.CharField(max_length=4, unique=True)
    stations = models.ManyToManyField(Station, related_name="clusters")
    station_groups = models.ManyToManyField(StationGroup, related_name="clusters")
    global_id = models.UUIDField(default=uuid.uuid4, unique=True)  # Globally unique ID


    def __str__(self):
        return f"Cluster {self.cluster_id}"

class Restriction(models.Model):
    restriction_code = models.CharField(max_length=2, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Restriction {self.restriction_code}"

class RestrictionDateBand(models.Model):
    restriction = models.ForeignKey(Restriction, on_delete=models.CASCADE, related_name="date_bands")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Date Band for Restriction {self.restriction.restriction_code}"

class TimeRestriction(models.Model):
    restriction = models.ForeignKey(Restriction, on_delete=models.CASCADE, related_name="time_restrictions")
    time_code = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    days_of_week = models.CharField(max_length=7)  # e.g., "MTWTFSS" for Mon-Sun

    def __str__(self):
        return f"Time Restriction {self.time_code} for {self.restriction.restriction_code}"

class TrainRestriction(models.Model):
    restriction = models.ForeignKey(Restriction, on_delete=models.CASCADE, related_name="train_restrictions")
    train_id = models.CharField(max_length=10)
    allowed_classes = models.CharField(max_length=3)  # e.g., "1" for first class, "2" for standard
    quota_controlled = models.BooleanField()
    weekend_first = models.BooleanField()

    def __str__(self):
        return f"Train Restriction {self.train_id} for {self.restriction.restriction_code}"
