import jwt
from rest_framework import generics, status
from ..utils.response import make_response, make_json_response
from src.models import ChatSession
from datetime import datetime, timedelta
from config.settings.conf import app_config

class GenerateTokenAPI(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        # Get browser_id from request data
        browser_id = kwargs.get('browser_id')
        
        if not browser_id:
             return make_response(
                "browser_id is required", status.HTTP_400_BAD_REQUEST, False
            )

        # Remove existing ChatSession for the given browser_id
        self.clean_existing_sessions(browser_id)

        # Create a new ChatSession
        chat_session = ChatSession.objects.create(browser_id=browser_id)

        # Generate a new JWT token
        token = self.generate_jwt_token(browser_id)

        # Return the new token and session information
        return make_json_response(
            {
                'token': token,
                'session_id': str(chat_session.id),
                'browser_id': browser_id,
                'created_at': chat_session.created_at.isoformat(),
            },
            "Token Generated Successfully",
            status.HTTP_201_CREATED,
            True,
        )

    @staticmethod
    def clean_existing_sessions(browser_id):
        # Remove existing ChatSession
        ChatSession.objects.filter(browser_id=browser_id).delete()

    @staticmethod
    def generate_jwt_token(browser_id):
        """Generate a JWT token with browser_id and an expiry time."""
        payload = {
            'browser_id': browser_id,
            'exp': datetime.now() + timedelta(minutes=app_config.JWT_TOKEN_TTL_IN_MINUTES)
        }
        return jwt.encode(payload, app_config.JWT_SECRET_KEY, algorithm=app_config.JWT_ALGORITHM)