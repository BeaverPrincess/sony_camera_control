import json
from camera.models import CameraInfo, API
from typing import Any, Tuple


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
        params = json.loads(params)
        payload["type"] = params["type"]
        param_options = params["params"]

        if len(param_options) == 1 and len(param_options[0]) == 1:
            json_object["params"] = [_conver_param_to_correct_type(param_options[0][0])]
        else:
            params_dict = {"type": params["type"], "params": param_options}
            return payload, params_dict
    else:
        json_object["params"] = []

    # Return the action list URL and the constructed JSON payload
    return payload, None


def _conver_param_to_correct_type(param: str) -> Any:
    if param.lower() == "true":
        return True

    if param.lower() == "false":
        return False

    if isinstance(param, int):
        return int(param)

    if isinstance(param, float):
        return float(param)

    return param
