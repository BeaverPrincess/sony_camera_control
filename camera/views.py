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
    def _retrieve_location_url(self) -> tuple[Optional[str], Optional[str]]:
        """
        Get location URL using SSDP M-Search.
        """
        # SSDP M-SEARCH request to discover the camera
        M_SEARCH = (
            b"M-SEARCH * HTTP/1.1\r\n"
            b"HOST: 239.255.255.250:1900\r\n"
            b'MAN: "ssdp:discover"\r\n'
            b"MX: 1\r\n"
            b"ST: urn:schemas-sony-com:service:ScalarWebAPI:1\r\n"
            b"USER-AGENT: Django/5.0 Python/3.x\r\n\r\n"
        )

        # Create socket for sending and receiving UDP packets over IPv4, necessary for SSDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # Allow socket to reuse the address and set socket options
        sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )  # Allows multiple sockets to bind to the same address and port -> in case OS hasnt closed the socket zb. from previous run
        sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_BROADCAST, 1
        )  # Extend to Broadcast
        sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_RCVBUF, 4096
        )  # Incease buffer size

        # Best to bind device IP directly ensures SSDP sends request through correct inteface
        local_ip = "192.168.122.177"
        sock.bind((local_ip, 0))

        # Send M-SEARCH requests multiple times to increase probability that camera reponses
        for i in range(5):
            sock.sendto(M_SEARCH, ("239.255.255.250", 1900))
            time.sleep(1)

        location_url = None
        start_time = time.time()
        timeout = 8  # Total timeout in seconds
        # Set a dynamic socket timeout to ensure that waiting for a response only takes exactly that long
        try:
            while True:
                # Calculate remaining time
                elapsed = time.time() - start_time
                remaining = timeout - elapsed
                if remaining <= 0:
                    break
                sock.settimeout(remaining)
                try:
                    data, addr = sock.recvfrom(1024)
                    response_str = data.decode("utf-8")
                    # Parse the response to get the LOCATION URL
                    for line in response_str.splitlines():
                        if line.startswith("LOCATION"):
                            location_url = line.split(" ", 1)[1]
                            break
                    if location_url:
                        break  # Exit loop if LOCATION URL is found
                except socket.timeout:
                    continue  # No data received, continue waiting
        except Exception as e:
            return None, f"Error: Failed to fetch location URL.\n{str(e)}"
        finally:
            sock.close()

        if not location_url:
            return None, "Error: Location URL not found in SSDP response."
        return location_url, None

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
        location_url, error = self._retrieve_location_url()
        if error:
            logging.error(error)
            return render(
                request,
                "camera_control.html",
                {"alert": "Fetching location URL failed."},
            )

        try:
            response = requests.get(location_url)
            if response.status_code == 200:
                xml_content = response.content

                # Parse the XML content
                camera_data, parse_error = self._parse_device_description(xml_content)
                if parse_error:
                    return render(
                        request, "camera_control.html", {"alert": parse_error}
                    )

                # Save the parsed data into the models
                success, save_error = self._save_camera_info(camera_data)
                if save_error:
                    return render(request, "camera_control.html", {"alert": save_error})

                return render(
                    request,
                    "camera_control.html",
                    {"alert": "Device description retrieved and saved successfully!"},
                )
            else:
                return render(
                    request,
                    "camera_control.html",
                    {"alert": "Error: Failed to fetch device description."},
                )

        except Exception as e:
            logging.error(f"Error: {str(e)}")
            return render(
                request,
                "camera_control.html",
                {"alert": f"Error: Failed to fetch device description."},
            )
