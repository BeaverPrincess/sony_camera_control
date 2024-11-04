from camera.models import CameraInfo, API
import json


def construct_api_payload(uuid: str, api: API):
    camera_info = CameraInfo.objects.get(uuid=uuid)
    action_list_url = camera_info.action_list_url + "/camera"
    # Fetch the model of the camera instace with the uuid -> get the supported api groups
    requested_model = camera_info.model
    supported_groups = requested_model.api_groups.values_list("group_name", flat=True)

    if api.group_name.group_name not in supported_groups:
        return None, f"Current model doesn't support the API {api.api_name}."

    json_object = api.json_object
    params = api.json_params

    if params:
        params = [_convert_param(param) for param in params.split(",")]
        if len(params) > 1:
            return None, "More than 1 param."  # temp
        json_object["params"] = params
    else:
        json_object["params"] = []

    # Return the action list URL and the constructed JSON payload
    return {
        "action": api.api_name,
        "action_list_url": action_list_url,
        "payload": json_object,
    }, None


def _convert_param(param: str) -> str | int | bool:
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
