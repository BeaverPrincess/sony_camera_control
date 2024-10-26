from django.shortcuts import render
from django.http import JsonResponse
import socket
import requests
from django.http import HttpResponse, HttpRequest, StreamingHttpResponse
from django.shortcuts import render
from django.conf import settings
from django.views import View
from camera.models import CameraInfo, CameraModel, API
import logging


class CameraControlView(View):
    """
    This Class View handles the functions on the server side for the controlling camera endpoint.
    """

    current_uuid = "uuid:000000001000-1010-8000-9AF17057BD5C"

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handle GET request from FE.
        Rightnow acts as default launch.
        """
        uuid = request.GET.get("uuid")
        self.current_uuid = uuid
        return render(request, "control_camera.html")

    def post(self, request: HttpRequest) -> JsonResponse:
        """
        Handle POST request from FE.
        """
        camera_info = CameraInfo.objects.get(uuid=self.current_uuid)
        action_list_url = camera_info.action_list_url + "/camera"

        action = request.POST.get("action")
        if not action:
            return JsonResponse({"error": "Invalid action."}, status=400)

        json_object, params = self._fetch_json_object(action)
        if json_object is None:
            return JsonResponse(
                {"error": f"Current model doesnt support the API {action}."},
                status=400,
            )

        if params:
            params = [self._convert_param(param) for param in params.split(",")]
            if len(params) > 1:
                return JsonResponse(
                    {"incompleted_json_object": json_object, "params": params},
                )
            json_object["params"] = [params]
        else:
            json_object["params"] = []

        # Return the action list URL and the constructed JSON payload
        response_data = {
            "action": action,
            "action_list_url": action_list_url,
            "payload": json_object,
        }

        return JsonResponse(response_data)

    def _fetch_json_object(self, api_to_fetch: str):
        """
        From the requested api, fetching its corresponding json object and params from the DB.
        """
        # Fetch the model of the camera instace with the uuid -> get the supported api groups
        requested_model = CameraInfo.objects.get(uuid=self.current_uuid).model
        supported_groups = requested_model.api_groups.values_list(
            "group_name", flat=True
        )
        # Fetch the API instance
        requested_api = API.objects.get(api_name=api_to_fetch)
        # If the API that the requested API belongs to also in the supported groups of the camera model.
        if requested_api.group_name.group_name in supported_groups:
            json_object = requested_api.json_object
            params = requested_api.json_params
            return json_object, params
        return None, None

    def _convert_param(self, param: str) -> str | int | bool:
        """
        API Params are saved in DB as string but they can either be str, int or bool depending on specific API.
        Convert a param into its actual type.
        """
        param = param.strip()
        if param.lower() == "true":
            return True
        elif param.lower() == "false":
            return False

        try:
            return int(param)
        except ValueError:
            pass

        try:
            return float(param)
        except ValueError:
            pass
        return param

    # def post(self, request: HttpRequest) -> HttpResponse:
    #     camera_info = (
    #         CameraInfo.objects.first()
    #     )  # Temporary since only 1 cam in DB, later will be filtered via UUID
    #     if not camera_info or not camera_info.action_list_url:
    #         return render(
    #             request, "control_camera.html", {"alert": "Camera not found in DB."}
    #         )
    #     mode = None
    #     liveview_url = None
    #     action_list_url = camera_info.action_list_url + "/camera"
    #     action = request.POST.get("action")

    #     if action == "start" or action == "stop":
    #         mode, response = self._toggle_rec_mode(request, action_list_url, action)
    #     elif action == "start_liveview" or action == "stop_liveview":
    #         mode, response, liveview_url = self._toggle_liveview(
    #             request, action_list_url, action
    #         )

    #     if response.status_code == 200:
    #         api_list = response.json()
    #         print(api_list)
    #         return render(
    #             request,
    #             "control_camera.html",
    #             {
    #                 "alert": "API sent successfully.",
    #                 "mode": mode,
    #                 "liveview_url": liveview_url,
    #             },
    #         )
    #     else:
    #         logging.error(f"Status code: {response.status_code}")
    #         return render(
    #             request,
    #             "control_camera.html",
    #             {"alert": "No response."},
    #         )

    # def _get_camera_status(self, request: HttpRequest, action_list_url: str) -> str:
    #     api_request_param = {
    #         "method": "getEvent",
    #         "params": [True],
    #         "id": 1,
    #         "version": "1.0",
    #     }
    #     response = requests.post(action_list_url, json=api_request_param)
    #     if response.status_code == 200:
    #         response_data = response.json()

    #         if "result" in response_data and len(response_data["result"]) > 0:
    #             return response_data["result"][0].get("cameraStatus", "Unknown")
    #     return "Error"

    # def _toggle_rec_mode(
    #     self, request: HttpRequest, action_list_url: str, action: str
    # ) -> HttpResponse:

    #     api_request_param = {
    #         "params": [],
    #         "id": 1,
    #         "version": "1.0",
    #     }

    #     if action == "start":
    #         api_request_param["method"] = "startRecMode"
    #         return "record", requests.post(action_list_url, json=api_request_param)

    #     elif action == "stop":
    #         api_request_param["method"] = "stopRecMode"
    #         return None, requests.post(action_list_url, json=api_request_param)

    # def _toggle_liveview(
    #     self, request: HttpRequest, action_list_url: str, action: str
    # ) -> HttpResponse:
    #     api_request_param = {
    #         "params": [],
    #         "id": 1,
    #         "version": "1.0",
    #     }

    #     if action == "start_liveview":
    #         api_request_param["method"] = "startLiveview"
    #         response = requests.post(action_list_url, json=api_request_param)
    #         if response.status_code == 200:
    #             response_data = response.json()
    #             print(f"Liveview link: {response_data}")
    #             liveview_url = response_data.get("result", [None])[0]
    #             return "liveview", response, liveview_url
    #         return "record", response, None

    #     else:
    #         api_request_param["method"] = "stopLiveview"
    #         return (
    #             "record",
    #             requests.post(action_list_url, json=api_request_param),
    #             None,
    #         )


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
