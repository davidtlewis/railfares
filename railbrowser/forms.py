from django import forms

class FindFaresForm(forms.Form):
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
