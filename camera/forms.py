from django import forms
from camera.models import API, APIGroup


class SandboxApiSelectionForm(forms.Form):
    api_name = forms.ModelChoiceField(
        queryset=API.objects.all(),
        label="Select an API",
        empty_label="Choose an API",
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class ControlGroupSelectionForm(forms.Form):
    group_name = forms.ModelChoiceField(
        queryset=APIGroup.objects.all(),
        label="Select an API-Group",
        empty_label="Choose an group",
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class CameraControlForm(forms.Form):
    action = forms.ChoiceField(label="Camera Action")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        api_choices = [(api.api_name, str(api)) for api in API.objects.all()]
        self.fields["action"].choices = api_choices
