from django import forms

class FindFaresForm(forms.Form):
    origin_name = forms.CharField(
        label="Origin Station",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter Origin Station Name",
            "class": "form-control",
            "data-autocomplete-url": "/station/autocomplete/",  # Set autocomplete endpoint
        }),
    )

    origin_code = forms.CharField(widget=forms.HiddenInput(), required=False)

    destination_name = forms.CharField(
        label="Destination Station",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter Destination Station Name",
            "class": "form-control",
            "data-autocomplete-url": "/station/autocomplete/",  # Set autocomplete endpoint
        }),
    )

    destination_code = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    single_fares_only = forms.BooleanField(
        label="Single Fares Only",
        required=False,
        initial=False,
    )

class FindFaresForm_old(forms.Form):
    origin = forms.CharField(
        max_length=4,
        label="Origin Station Code",
        widget=forms.TextInput(attrs={'placeholder': 'Enter Origin Code'}),
        required=True,
    )
    destination = forms.CharField(
        max_length=4,
        label="Destination Station Code",
        widget=forms.TextInput(attrs={'placeholder': 'Enter Destination Code'}),
        required=True,
    )
    single_fares_only = forms.BooleanField(
        label="Single Fares Only",
        required=False,
        initial=False,
    )

class RouteSearchForm(forms.Form):
    route_code = forms.CharField(label='Route Code', max_length=5, required=False)
    description = forms.CharField(label='Description', max_length=16, required=False)

class ClusterSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        label="Search Clusters",
        widget=forms.TextInput(attrs={"placeholder": "Enter Cluster ID or Name", "class": "form-control"}),
    )

class StationSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        label="Search Stations",
        widget=forms.TextInput(attrs={"placeholder": "Enter Station Code or Name", "class": "form-control"}),
    )

class StationGroupSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        label="Search Station Groups",
        widget=forms.TextInput(attrs={"placeholder": "Enter Group ID or Name", "class": "form-control"}),
    )

class FlowSearchForm(forms.Form):
    flow_id = forms.CharField(
        max_length=7,
        min_length=7,
        required=False,
        label="Flow ID",
        widget=forms.NumberInput(attrs={"placeholder": "Enter Flow ID", "class": "form-control"}),
    )
    origin = forms.CharField(
        max_length=100,
        required=False,
        label="Origin Name/Code",
        widget=forms.TextInput(attrs={"placeholder": "Enter Origin Name or Code", "class": "form-control"}),
    )
    destination = forms.CharField(
        max_length=100,
        required=False,
        label="Destination Name/Code",
        widget=forms.TextInput(attrs={"placeholder": "Enter Destination Name or Code", "class": "form-control"}),
    )
