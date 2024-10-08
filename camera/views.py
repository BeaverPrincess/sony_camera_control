from django.shortcuts import render
from django.http import JsonResponse
import socket
import requests
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.conf import settings
from django.views import View
from typing import Optional
import xml.etree.ElementTree as ET
from .models import CameraInfo
import time
import logging
from .models import CameraModel
import json


class CameraControlView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "camera_control.html")


class FetchDeviceDescriptionView(View):
    def _parse_device_description(
        self, xml_content: bytes
    ) -> tuple[Optional[dict], Optional[str]]:
        """
        Parse the XML content and extract necessary information.

        Return:
            Extracted model name, uuid and action list url from device description
        """
        try:
            # Parse the XML content from the given bytes.
            root = ET.fromstring(xml_content)
            # Extract the namespace from the root tag.
            namespace = root.tag[root.tag.find("{") : root.tag.find("}") + 1]

            # Find 'friendlyName' and 'UDN' tags aka model and uuid
            model = root.find(f".//{namespace}friendlyName").text
            uuid = root.find(f".//{namespace}UDN").text

            # Adjust namepspace for action list url and search for it
            scalar_namespace = {"av": "urn:schemas-sony-com:av"}
            action_list_url = root.find(
                ".//av:X_ScalarWebAPI_ActionList_URL", namespaces=scalar_namespace
            ).text

            return {
                "model": model,
                "uuid": uuid,
                "action_list_url": action_list_url,
            }, None

        except ET.ParseError:
            return None, "Error: Failed to parse XML content."
        except Exception as e:
            return (
                None,
                f"Error: An unexpected error occurred while parsing XML.\n{str(e)}",
            )

    def _save_camera_info(self, camera_data: dict) -> tuple[bool, Optional[str]]:
        """
        Save camera info and services to the database.
        """
        try:
            try:  # This tell the data base to get the object from CameraModel table with the extracted model from the xml
                camera_model = CameraModel.objects.get(model=camera_data["model"])
            except CameraModel.DoesNotExist:
                return (
                    False,
                    f"Error: Camera model '{camera_data['model']}' not found in the database.",
                )

            # Model from CameraModel founded -> Search in CameraInfo for object with the same uuid -> if founded then update else create (this means new device)
            CameraInfo.objects.update_or_create(
                uuid=camera_data["uuid"],
                defaults={
                    "model": camera_model,
                    "uuid": camera_data["uuid"],
                    "action_list_url": camera_data["action_list_url"],
                },
            )

            return True, None
        except Exception as e:
            return (
                False,
                f"Error: Failed to save camera info to the database.\n{str(e)}",
            )

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Expects POST request to this Class View, in our case request containing the XML Device Description
        """
        try:
            # Extract device description from the post request
            device_description = request.POST.get("device_description")
            if not device_description:
                return render(
                    request,
                    "camera_control.html",
                    {"alert": "No device description found in request."},
                )

            # Extract model name, uuid and action list url from device description
            camera_data, parse_error = self._parse_device_description(
                device_description
            )
            if parse_error:
                logging.error(parse_error)
                return render(
                    request,
                    "camera_control.html",
                    {"alert": "Parsing device discription failed."},
                )

            # Save model name, uuid and action list in table keeping track of what devices have connected to this Server
            success, save_error = self._save_camera_info(camera_data)
            if save_error:
                return render(request, "camera_control.html", {"alert": save_error})

            return render(
                request,
                "camera_control.html",
                {"alert": "Device description retrieved and saved successfully!"},
            )
        except Exception as e:
            return render(
                request,
                "camera_control.html",
                {"alert": f"Error: {e}."},
            )


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
