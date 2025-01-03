from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.views import View
from typing import Optional
import xml.etree.ElementTree as ET
from camera.models import CameraInfo
import logging
from camera.models import CameraModel
from camera.enums import CameraModes


class CameraConnectView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "connect_camera.html")


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
                    f"Error: Camera model '{camera_data['model']}' is not supported.",
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
                    "connect_camera.html",
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
                    "connect_camera.html",
                    {"alert": "Parsing device discription failed."},
                )

            # Save model name, uuid and action list in table keeping track of what devices have connected to this Server
            success, save_error = self._save_camera_info(camera_data)
            if save_error:
                return render(request, "connect_camera.html", {"alert": save_error})

            ## TO-DO: Implement a way to pass the uuid to the control view

            return render(
                request,
                "connect_camera.html",
                {
                    "alert": f"Device description retrieved and saved successfully!\nUUID: {camera_data["uuid"]}",
                    "uuid": camera_data["uuid"],
                    "mode": CameraModes.Record,
                },
            )
        except Exception as e:
            return render(
                request,
                "connect_camera.html",
                {"alert": f"Error: {e}."},
            )
