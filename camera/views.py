from django.shortcuts import render, JsonResponse
import requests

# Create your views here.
def get_camera_info(request):
    url = "http://192.168.122.1/sony/camera"  # Replace with the camera's IP address
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "method": "getApplicationInfo",
        "params": [],
        "id": 1,
        "version": "1.0"
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()
        return JsonResponse(response_data)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)