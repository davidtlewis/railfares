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
