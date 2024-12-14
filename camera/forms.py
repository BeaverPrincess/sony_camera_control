from django import forms
from camera.models import API, APIGroup


class SandboxApiSelectionForm(forms.Form):
    """
    Form to choose api from all.
    """

    api_name = forms.ModelChoiceField(
        queryset=API.objects.all(),
        label="Select an API",
        empty_label="Choose an API",
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class CameraControlForm(forms.Form):
    """
    Form to choose api by navigating through the api groups.
    """

    group = forms.ChoiceField(label="API Group")
    action = forms.ChoiceField(label="Camera Action")
    isLiveView = forms.BooleanField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate group choices
        self.fields["group"].choices = [
            (group.id, group.group_name) for group in APIGroup.objects.all()
        ]

        # when bounded aka submitted with a group choice -> populate api choices accordingly -> else empty
        if self.is_bound:
            group_id = self.data.get("group")
            if group_id:
                group_id = int(group_id)
                apis = API.objects.filter(group_name_id=group_id)
                self.fields["action"].choices = [(api.id, str(api)) for api in apis]
            else:
                self.fields["action"].choices = []
        else:
            self.fields["action"].choices = []

        self.fields["group"].widget.attrs.update({"id": "id_group"})
        self.fields["action"].widget.attrs.update({"id": "id_action"})
