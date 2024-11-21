import jwt
from rest_framework import generics, status
from ..utils.response import make_response
from src.models import ChatSession
from config.settings.conf import app_config

class InvalidateTokenAPI(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        try:
            token = request.headers['Authorization'].split()[-1]
            if not token:
                return make_response(
                    "Token is required.", status.HTTP_400_BAD_REQUEST, False
                )
            remove_existing_session(token)
            return make_response(
                "Session removed successfully.", status.HTTP_200_OK, True
            )
        except KeyError:
            return make_response(
                "Authorization header is missing.", status.HTTP_400_BAD_REQUEST, False
            )
        except Exception as e:
            return make_response(
                f"An error occurred: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR, False
            )
    
def remove_existing_session(jwt_token):
    """Validate the JWT token and remove sessions."""
    try:
        payload = jwt.decode(jwt_token, app_config.JWT_SECRET_KEY, algorithms=[app_config.JWT_ALGORITHM])

        # Here, you can also check if the browser_id matches a session
        browser_id = payload.get("browser_id")
        if not browser_id:
            return False
        
        # Remove existing ChatSession
        ChatSession.objects.filter(browser_id=browser_id).delete()
        return True
    
    except Exception as e:
        print("error in remove_existing_session:", e)
        return False