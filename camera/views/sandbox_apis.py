from django.http import JsonResponse
from django.views.generic.edit import FormView
from camera.forms import SandboxApiSelectionForm
from camera.views.helper_functions.api_json_retrieval import construct_api_payload
import json


class SandboxApiSelectionView(FormView):
    template_name = "sandbox_apis.html"
    form_class = SandboxApiSelectionForm
    action_list_url = "http://192.168.122.1:8080/sony/camera"

    def dispatch(self, request, *args, **kwargs):
        # Extract 'uuid' from GET parameters
        self.uuid = request.GET.get("uuid")
        print(f"UUID in sandbox: {self.uuid}")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        selected_api = form.cleaned_data["api_name"]
        payload, error = construct_api_payload(self.uuid, selected_api)

        if not payload and error:
            return JsonResponse({"error": error})
            # return self.render_to_response(
            #     self.get_context_data(form=form, error=error)
            # )  # Not supported API

        if payload and error:
            return JsonResponse({"payload": payload, "params": error})
            # return self.render_to_response(
            #     self.get_context_data(form=form, params=payload)
            # )  # More than 1 param -> need to choose ## to be implemented
        # payload["payload"] = json.dumps(payload["payload"])
        return JsonResponse({"payload": payload})
        # return self.render_to_response(self.get_context_data(form=form, api=payload))
