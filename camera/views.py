from django.shortcuts import render
from django.http import JsonResponse
import socket
import requests
from django.http import HttpResponse
from django.shortcuts import render


def camera_control(request):
    return render(request, "camera_control.html")


def fetch_device_description(request):
    # SSDP M-SEARCH request to discover the camera
    M_SEARCH = (
        b"M-SEARCH * HTTP/1.1\r\n"
        b"HOST: 239.255.255.250:1900\r\n"
        b'MAN: "ssdp:discover"\r\n'
        b"MX: 1\r\n"
        b"ST: urn:schemas-sony-com:service:ScalarWebAPI:1\r\n"
        b"USER-AGENT: Django/4.0 Python/3.x\r\n\r\n"
    )

    # Create a socket for the SSDP M-SEARCH
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.settimeout(2)
    sock.sendto(M_SEARCH, ("239.255.255.250", 1900))

    try:
        # Receive the camera's response
        data, addr = sock.recvfrom(1024)
        response_str = data.decode("utf-8")
        location_url = None

        # Parse the response to get the LOCATION header
        for line in response_str.splitlines():
            if line.startswith("LOCATION"):
                location_url = line.split(" ", 1)[1]
                break

        if not location_url:
            return render(
                request,
                "camera_control.html",
                {"alert": "Device description fetching failed."},
            )

        # Fetch the device description from the LOCATION URL
        response = requests.get(location_url)
        if response.status_code == 200:
            xml_content = response.content
            return render(
                request, "camera_control.html", {"alert": xml_content.decode("utf-8")}
            )
        else:
            return render(
                request,
                "camera_control.html",
                {"alert": "Error: Failed to fetch device description."},
            )

    except socket.timeout:
        return render(
            request,
            "camera_control.html",
            {"alert": "Error: Failed to fetch device description."},
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        return render(
            request,
            "camera_control.html",
            {"alert": f"Error: Failed to fetch device description.\n{str(e)}"},
        )
