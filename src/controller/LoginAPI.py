import jwt
from rest_framework import generics, status
from ..utils.response import make_response, make_json_response
from django.contrib.auth import authenticate
from datetime import datetime, timedelta
from config.settings.conf import app_config

class LoginAPI(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        # Get browser_id from request data
        data = request.data.copy()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
             return make_response(
                "UserName and Password is required", status.HTTP_400_BAD_REQUEST, False
            )


        # Create a new ChatSession
        user = authenticate(username=username, password=password)

        if not user:
            return make_response(
                "Invalid credentials", status.HTTP_401_UNAUTHORIZED, False
            )
        
        # Generate a new JWT token
        token = self.generate_jwt_token(user.id)

        # Return the new token and session information
        return make_json_response(
            {
                'username': user.username,
                'logintoken': token,
                'created_at': datetime.now().isoformat(),
            },
            "Login Successfully",
            status.HTTP_200_OK,
            True,
        )

    def generate_jwt_token(self,user_id):
        """Generate a JWT token with user_id and an expiry time."""
        payload = {
            'user_id': user_id,
            'exp': datetime.now() + timedelta(minutes=app_config.JWT_TOKEN_TTL_IN_MINUTES)
        }
        return jwt.encode(payload, app_config.JWT_SECRET_KEY, algorithm=app_config.JWT_ALGORITHM)