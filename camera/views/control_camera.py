from django.http import HttpResponse, HttpRequest
from camera.models import API, APIGroup
from camera.views.helper_functions.api_json_retrieval import (
    construct_api_payload,
)
from django.views.generic.edit import FormView
from camera.forms import CameraControlForm
from django.views import View
from django.http import JsonResponse


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
        ### TO-DO: Handle is live view with live view size
        is_live_view = form.cleaned_data["isLiveView"]
        
        if int(api_id) == API.objects.get(api_name="startLiveviewWithSize").id and is_live_view:
            return JsonResponse({"error": "Please turn Live View off first!"})

        selected_api = API.objects.get(id=api_id)
        payload, error = construct_api_payload(current_uuid, selected_api)

        # On error
        if not payload and error:
            return JsonResponse({"error": error})

        # On json with multiple params -> required user to choose which one.
        # error now holds the params.
        if payload and error:
            return JsonResponse({"payload": payload, "params": error})

        # No param
        return JsonResponse({"payload": payload})


{
    "result": [
        {
            "type": "availableApiList",
            "names": [
                "getVersions",
                "getMethodTypes",
                "getApplicationInfo",
                "getAvailableApiList",
                "getEvent",
                "actTakePicture",
                "stopRecMode",
                "startLiveview",
                "stopLiveview",
                "startLiveviewWithSize",
                "actZoom",
                "actHalfPressShutter",
                "cancelHalfPressShutter",
                "setSelfTimer",
                "getSelfTimer",
                "getAvailableSelfTimer",
                "getSupportedSelfTimer",
                "getSupportedContShootingMode",
                "getSupportedContShootingSpeed",
                "setExposureMode",
                "getAvailableExposureMode",
                "getExposureMode",
                "getSupportedExposureMode",
                "setExposureCompensation",
                "getExposureCompensation",
                "getAvailableExposureCompensation",
                "getSupportedExposureCompensation",
                "setFNumber",
                "getFNumber",
                "getAvailableFNumber",
                "getSupportedFNumber",
                "setIsoSpeedRate",
                "getIsoSpeedRate",
                "getAvailableIsoSpeedRate",
                "getSupportedIsoSpeedRate",
                "getLiveviewSize",
                "getAvailableLiveviewSize",
                "getSupportedLiveviewSize",
                "setPostviewImageSize",
                "getPostviewImageSize",
                "getAvailablePostviewImageSize",
                "getSupportedPostviewImageSize",
                "getSupportedProgramShift",
                "setShootMode",
                "getShootMode",
                "getAvailableShootMode",
                "getSupportedShootMode",
                "getShutterSpeed",
                "getAvailableShutterSpeed",
                "getSupportedShutterSpeed",
                "setTouchAFPosition",
                "getTouchAFPosition",
                "setWhiteBalance",
                "getWhiteBalance",
                "getSupportedWhiteBalance",
                "getAvailableWhiteBalance",
                "getSupportedFlashMode",
                "setFocusMode",
                "getFocusMode",
                "getAvailableFocusMode",
                "getSupportedFocusMode",
                "setZoomSetting",
                "getAvailableZoomSetting",
                "getZoomSetting",
                "getSupportedZoomSetting",
                "getStorageInformation",
                "setLiveviewFrameInfo",
                "getLiveviewFrameInfo",
            ],
        },
        {"cameraStatus": "IDLE", "type": "cameraStatus"},
        {
            "zoomPositionCurrentBox": 0,
            "type": "zoomInformation",
            "zoomIndexCurrentBox": 0,
            "zoomNumberBox": 1,
            "zoomPosition": 0,
        },
        {"type": "liveviewStatus", "liveviewStatus": False},
        None,
        [],
        [],
        None,
        None,
        None,
        [
            {
                "storageDescription": "Storage Media",
                "numberOfRecordableImages": 4134,
                "type": "storageInformation",
                "storageID": "Memory Card 1",
                "recordTarget": True,
                "recordableTime": -1,
            }
        ],
        None,
        {
            "cameraFunctionCandidates": ["Contents Transfer", "Remote Shooting"],
            "type": "cameraFunction",
            "currentCameraFunction": "Remote Shooting",
        },
        None,
        None,
        None,
        None,
        None,
        {
            "exposureModeCandidates": [
                "Program Auto",
                "Aperture",
                "Shutter",
                "Manual",
                "Intelligent Auto",
            ],
            "type": "exposureMode",
            "currentExposureMode": "Aperture",
        },
        {
            "postviewImageSizeCandidates": ["Original", "2M"],
            "type": "postviewImageSize",
            "currentPostviewImageSize": "2M",
        },
        {"currentSelfTimer": 2, "type": "selfTimer", "selfTimerCandidates": [0, 2, 10]},
        {
            "shootModeCandidates": ["still"],
            "type": "shootMode",
            "currentShootMode": "still",
        },
        None,
        None,
        None,
        {
            "minExposureCompensation": -9,
            "type": "exposureCompensation",
            "stepIndexOfExposureCompensation": 1,
            "maxExposureCompensation": 9,
            "currentExposureCompensation": -9,
        },
        {"type": "flashMode", "flashModeCandidates": [], "currentFlashMode": "on"},
        {
            "fNumberCandidates": [
                "3.5",
                "4.0",
                "4.5",
                "5.0",
                "5.6",
                "6.3",
                "7.1",
                "8.0",
                "9.0",
                "10",
                "11",
                "13",
                "14",
                "16",
                "18",
                "20",
                "22",
            ],
            "type": "fNumber",
            "currentFNumber": "5.6",
        },
        {
            "focusModeCandidates": ["AF-S", "DMF", "MF"],
            "type": "focusMode",
            "currentFocusMode": "AF-S",
        },
        {
            "type": "isoSpeedRate",
            "isoSpeedRateCandidates": [
                "AUTO",
                "100",
                "125",
                "160",
                "200",
                "250",
                "320",
                "400",
                "500",
                "640",
                "800",
                "1000",
                "1250",
                "1600",
                "2000",
                "2500",
                "3200",
                "4000",
                "5000",
                "6400",
                "8000",
                "10000",
                "12800",
                "16000",
            ],
            "currentIsoSpeedRate": "AUTO",
        },
        None,
        {"type": "programShift", "isShifted": False},
        {
            "type": "shutterSpeed",
            "shutterSpeedCandidates": [],
            "currentShutterSpeed": "1/4",
        },
        {
            "type": "whiteBalance",
            "currentColorTemperature": -1,
            "checkAvailability": True,
            "currentWhiteBalanceMode": "Auto WB",
        },
        None,
    ],
    "id": 1,
}
