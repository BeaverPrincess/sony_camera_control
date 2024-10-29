from django.views.generic.edit import FormView
from django.shortcuts import render
from camera.forms import SandboxApiSelectionForm
from camera.views.helper_functions.api_json_retrieval import (
    fetch_json_object,
    convert_param,
)


class SandboxApiSelectionView(FormView):
    template_name = "sandbox_apis.html"
    form_class = SandboxApiSelectionForm
    uuid = "uuid:000000001000-1010-8000-9AF17057BD5C"
    action_list_url = "http://192.168.122.1:8080/sony/camera"

    def form_valid(self, form):
        selected_api = form.cleaned_data["api_name"]

        json_object, params = fetch_json_object(self.uuid, selected_api.api_name)
        if json_object is None:
            return self.render_to_response(
                self.get_context_data(
                    form=form, error="No json object received from DB."
                )
            )

        if params:
            params = [convert_param(param) for param in params.split(",")]
            if len(params) > 1:
                return self.render_to_response(
                    self.get_context_data(form=form, error="More than 1 param.")
                )
            json_object["params"] = [params]
        else:
            json_object["params"] = []

        # Return the action list URL and the constructed JSON payload
        response_data = {
            "action": selected_api.api_name,
            "action_list_url": self.action_list_url,
            "payload": json_object,
        }

        return self.render_to_response(
            self.get_context_data(form=form, api=response_data)
        )
