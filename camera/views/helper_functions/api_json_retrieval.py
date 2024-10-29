from camera.models import CameraInfo, API


def fetch_json_object(uuid: str, api_to_fetch: str):
    """
    From the requested api, fetching its corresponding json object and params from the DB.
    """
    # Fetch the model of the camera instace with the uuid -> get the supported api groups
    requested_model = CameraInfo.objects.get(uuid=uuid).model
    supported_groups = requested_model.api_groups.values_list("group_name", flat=True)
    # Fetch the API instance
    requested_api = API.objects.get(api_name=api_to_fetch)
    # If the API that the requested API belongs to also in the supported groups of the camera model.
    if requested_api.group_name.group_name in supported_groups:
        json_object = requested_api.json_object
        params = requested_api.json_params
        return json_object, params
    return None, None


def convert_param(param: str) -> str | int | bool:
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
