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
from .models import CameraInfo, CameraService
import time
import logging


class CameraControlView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "camera_control.html")


class FetchDeviceDescriptionView(View):
    def _get_namespace(self, element) -> str:
        """
        Extracts the namespace from an XML element.
        """
        # The namespace is enclosed in curly braces within the tag
        namespace_uri = element.tag[element.tag.find("{") : element.tag.find("}") + 1]
        return namespace_uri

    def _parse_device_description(
        self, xml_content: bytes
    ) -> tuple[Optional[dict], Optional[str]]:
        """
        Parse the XML content and extract necessary information.
        """
        try:
            root = ET.fromstring(xml_content)
            namespace = self._get_namespace(root)

            # Extract device infos
            friendly_name = root.find(f".//{namespace}friendlyName").text
            uuid = root.find(f".//{namespace}UDN").text
            model = root.find(f".//{namespace}modelName").text

            # Extract ScalarWebAPI namespace for specific elements
            scalar_namespace = {"av": "urn:schemas-sony-com:av"}
            action_list_url = root.find(
                ".//av:X_ScalarWebAPI_ActionList_URL", namespaces=scalar_namespace
            ).text

            # Extract service types
            service_types = [
                service.find(
                    "av:X_ScalarWebAPI_ServiceType", namespaces=scalar_namespace
                ).text
                for service in root.findall(
                    ".//av:X_ScalarWebAPI_Service", namespaces=scalar_namespace
                )
            ]

            return {
                "friendly_name": friendly_name,
                "uuid": uuid,
                "model": model,
                "action_list_url": action_list_url,
                "service_types": service_types,
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
            camera_info, _ = CameraInfo.objects.update_or_create(
                uuid=camera_data["uuid"],
                defaults={
                    "friendly_name": camera_data["friendly_name"],
                    "model": camera_data["model"],
                    "action_list_url": camera_data["action_list_url"],
                },
            )

            CameraService.objects.update_or_create(
                camera_info=camera_info,
                defaults={"service_types": ",".join(camera_data["service_types"])},
            )

            return True, None
        except Exception as e:
            return (
                False,
                f"Error: Failed to save camera info to the database.\n{str(e)}",
            )

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Use location URL to fetch the device description, parse it, and save to the database.
        """
        try:
            response = requests.get("http://localhost:8001/discover")
            if response.status_code == 200:
                data = response.json()
                error_alert = ""
                if "error" in data:
                    error_alert = data["error"]
                else:
                    device_description = data.get("device_description")
                    print(device_description)
            else:
                error_alert = "Failed to fetch device description from local service."
        except Exception as e:
            error_alert = f"Error: {str(e)}"

        if not error_alert:
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
            success, save_error = self._save_camera_info(camera_data)
            if save_error:
                return render(request, "camera_control.html", {"alert": save_error})

            return render(
                request,
                "camera_control.html",
                {"alert": "Device description retrieved and saved successfully!"},
            )
        else:
            logging.error(error_alert)
            return render(
                request,
                "camera_control.html",
                {"alert": "Error at retrieving device descriptions."},
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
