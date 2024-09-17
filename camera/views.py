from django.shortcuts import render
from django.http import JsonResponse
import socket


# SSDP M-SEARCH to discover the camera
def discover_camera(request):
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
        return JsonResponse({"status": "success", "data": data.decode("utf-8")})
    except socket.timeout:
        return JsonResponse(
            {"status": "error", "message": "No response received from the camera"}
        )


# Function to handle a basic API call
def api_call(request):
    # For now, let's mock this call
    # You'd use something like requests.post to call the real API endpoint discovered in SSDP
    camera_api_url = (
        "http://192.168.122.1:8080/sony/system"  # Example URL after discovery
    )

    # Simulating a simple API call (e.g., getting the API version)
    # In a real-world scenario, you'd use requests.post() here.
    api_response = {"result": ["1.0"], "id": 1}

    return JsonResponse({"status": "success", "data": api_response})


# View for displaying buttons
def camera_control(request):
    return render(request, "camera_control.html")
