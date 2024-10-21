from django.shortcuts import render
from django.http import JsonResponse
import socket
import requests
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.conf import settings
from django.views import View
from camera.models import CameraInfo
import logging

class CameraControlView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "connect_camera.html")

class GetAvailableApiListView(View):
    def get(self, request):
        camera_info = (
            CameraInfo.objects.first()
        )  # Temporary since only 1 cam in DB, later will be filtered via UUID
        if not camera_info or not camera_info.action_list_url:
            return render(
                request, "camera_control.html", {"alert": "Camera not found in DB."}
            )

        action_list_url = camera_info.action_list_url + "/camera"

        api_request_param = {
            "method": "stopRecMode",
            "params": [],
            "id": 1,
            "version": "1.0",
        }

        response = requests.post(action_list_url, json=api_request_param)

        if response.status_code == 200:
            api_list = response.json()
            print(api_list)
            return render(
                request,
                "camera_control.html",
                {"alert": "Available API list received successfully."},
            )
        else:
            logging.error(f"Status code: {response.status_code}")
            return render(
                request,
                "camera_control.html",
                {"alert": "No response for available APIs."},
            )
