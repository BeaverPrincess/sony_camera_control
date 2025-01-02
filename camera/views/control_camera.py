from django.http import HttpResponse, HttpRequest
from camera.models import API, APIGroup
from camera.views.helper_functions.api_json_retrieval import (
    construct_api_payload,
)
from django.views.generic.edit import FormView
from camera.forms import CameraControlForm
from django.views import View
from django.http import JsonResponse
from camera.enums import CameraModes


class APIListView(View):
    """
    Uses to load apis with given group id.
    Gets called on changes in group choice -> get apis dymically without reloading the form.
    """

    def get(self, request, *args, **kwargs):
        group_id = request.GET.get("group_id")
        if group_id:
            group = APIGroup.objects.get(id=group_id)
            apis = group.apis.all()
            api_list = [{"id": api.id, "name": str(api)} for api in apis]
            return JsonResponse({"apis": api_list})
        else:
            return JsonResponse({"error": "No group id provided"}, status=400)


class CameraControlView(FormView):
    """
    Handle main control mode's form submission.
    """

    template_name = "control_camera.html"
    form_class = CameraControlForm
    current_mode = {
        CameraModes.LiveView: 0,
        CameraModes.Record: 0,
        CameraModes.StillShoot: 0,
    }

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Each time a GET or POST request is made, Django will make a new instance of the view
        We would need to pass the uuid from the GET request (sent from the control mode triggering button) to the context
        to make it usable in the template and have to passed as input each time a Post request is made (form_valid executes on POST)
        """
        context = super().get_context_data(**kwargs)
        context["current_uuid"] = self.request.GET.get("uuid")
        return context

    def form_valid(self, form):
        """
        Fetch the submited API and construct the required JSON and url action list to make the API call.
        """
        api_id = form.cleaned_data["action"]
        current_uuid = self.request.POST.get("uuid")

        self.current_mode[CameraModes.LiveView] = form.cleaned_data["isLiveView"]
        self.current_mode[CameraModes.Record] = form.cleaned_data["isRecord"]
        self.current_mode[CameraModes.StillShoot] = form.cleaned_data["isStillShooting"]

        selected_api = API.objects.get(id=api_id)

        # If the requested API required a mode and its not one 
        if selected_api.required_mode and not self.current_mode[selected_api.required_mode]:
            return JsonResponse({"error": f"Only available in {selected_api.required_mode} mode!"})

        payload, error = construct_api_payload(current_uuid, selected_api)

        # On error
        if not payload and error:
            return JsonResponse({"error": error})

        # On json with multiple params -> required user to choose which one.
        # error now holds the params.
        if payload and error:
            return JsonResponse({"payload": payload, "params": error})

        # No param or 1 param only
        return JsonResponse({"payload": payload})

    def _validate_action_and_current_mode(self, selected_api: API) -> bool:
        """Compare selected api's required mode with the equivalent current mode"""
        if selected_api.required_mode not in self.current_mode:
            return False
        return True
