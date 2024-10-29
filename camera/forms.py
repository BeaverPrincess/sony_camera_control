from django import forms
from camera.models import API


class SandboxApiSelectionForm(forms.Form):
    api_name = forms.ModelChoiceField(
        queryset=API.objects.all(),
        label="Select an API",
        empty_label="Choose an API",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    

