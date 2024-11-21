from rest_framework.renderers import JSONRenderer
from config.settings.conf import app_config

class APIRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            data = {}

        status_code = renderer_context["response"].status_code
        response = {
            **data,
            "latest_version": app_config.LATEST_VERSION,
            "acceptable_version": app_config.ACCEPTABLE_VERSION,
        }

        if status_code >= 400:
            response["success"] = False
            try:
                response["message"] = data["detail"]
            except KeyError:
                response["data"] = data

        return super(APIRenderer, self).render(
            response, accepted_media_type, renderer_context
        )
