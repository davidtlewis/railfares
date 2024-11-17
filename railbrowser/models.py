from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

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
    origin_object_id = models.PositiveIntegerField(null=True)
    origin = GenericForeignKey('origin_content_type', 'origin_object_id')
    
    # Generic Foreign Key setup for Destination
    destination_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="destination_flows", null=True)
    destination_object_id = models.PositiveIntegerField(null=True)
    destination = GenericForeignKey('destination_content_type', 'destination_object_id')
    
    # Other fields as before
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
    
    def __str__(self):
        origin_name = self.origin if self.origin else "Unknown"
        destination_name = self.destination if self.destination else "Unknown"
        return f"Flow from {origin_name} to {destination_name}"


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
    nlc_code = models.CharField(max_length=4, unique=True)  # National Location Code
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"Station {self.nlc_code}: {self.name}"

class StationCluster(models.Model):
    cluster_id = models.CharField(max_length=4, unique=True)
    stations = models.ManyToManyField(Station, related_name="clusters")

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
