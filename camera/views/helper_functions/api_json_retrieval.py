from camera.models import CameraInfo, API
from typing import Tuple


def construct_api_payload(uuid: str, api: API) -> Tuple[None | dict, None | list | str]:
    """
    Construct json object for API call based on choosen action.
    If error -> None, str.
    If 1 or less param -> dict, None.
    If more than 1 param -> dict, list. (The list of params needs to be returned to be choosen by user)
    """
    camera_info = CameraInfo.objects.get(uuid=uuid)
    action_list_url = camera_info.action_list_url + "/camera"
    # Fetch the model of the camera instace with the uuid -> get the supported api groups
    requested_model = camera_info.model
    supported_groups = requested_model.api_groups.values_list("group_name", flat=True)

    if api.group_name.group_name not in supported_groups:
        return None, f"Current model doesn't support the API {api.api_name}."

    json_object = api.json_object
    params = api.json_params

    payload = {
        "action": api.api_name,
        "action_list_url": action_list_url,
        "payload": json_object,
    }

    if params:
        # ; indicates user needs to choose between the parameters
        if ";" in params:
            if api.api_name == "setIsoSpeedRate":
                params = params.split(";")
                return payload, params
            params = [_convert_param(param) for param in params.split(";")]
            return payload, params
        # pure number indicates a manual input is required, the number is the number of inputs needed.
        elif isinstance(_convert_param(params), int):
            json_object["params"] = _convert_param(params)
            return payload, params
        else:
            json_object["params"] = params
    else:
        json_object["params"] = ""

    # Return the action list URL and the constructed JSON payload
    return payload, None


def _convert_param(param: str) -> str | int | bool:
    """
    API Params are saved in DB as string but they can either be str, int or bool depending on specific API.
    Convert a param into its actual type.
    """
    param = param.strip()
    if param.lower() == "true" or param.lower() == "false":
        return param.lower()

    try:
        return int(param)
    except ValueError:
        pass

    try:
        return float(param)
    except ValueError:
        pass
    return param
