import jwt
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from src.models.ChatSession import ChatSession
from config.settings.conf import app_config

class CustomerIDMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope["error"] = None
        jwt_token = None
        
        # Get the userToken from the headers
        for item in scope.get("headers", []):
            key, value = item
            if key == b"authorization":
                jwt_token_str = value.decode()
                jwt_token = jwt_token_str.replace("Token ", "")
                break
            elif key == b"sec-websocket-protocol": 
                decoded_value = value.decode()
                parts = decoded_value.split(', ')
    
                # Check if there are two parts or just one
                if len(parts) == 2:
                    jwt_token, thread_id = parts
                else:
                    jwt_token = parts[0]
                    thread_id = None

        # NOTE: Authentication Functionality
        if jwt_token:
            try:
                if not await self.validate_jwt(jwt_token):
                    scope["error"] = "Invalid token"
            except ValueError:
                scope["error"] = ValueError("Invalid token passed")

        if not jwt_token: 
            scope["error"] = "Token not provided"

        return await self.app(scope, receive, send)


    @database_sync_to_async
    def validate_jwt(self, jwt_token):
        """Validate the JWT token and check its expiration."""
        try:
            # Decode the token using your secret key and algorithms
            payload = jwt.decode(jwt_token, app_config.JWT_SECRET_KEY, algorithms=[app_config.JWT_ALGORITHM])
            # Here, you can also check if the browser_id matches a session
            browser_id = payload.get("browser_id")
            if not browser_id:
                return False
            
            # Optional: Check if the browser_id exists in the ChatSession model
            session_exists = ChatSession.objects.filter(browser_id=browser_id, is_active=True).exists()

            return session_exists

        except Exception as e:
            # Handle any other exceptions
            print("error in validate_jwt:", e)
            return False


    # def extract_jwt_token(self, scope):
    #     query_string = scope['query_string'].decode('utf-8')
    #     query_params = parse_qs(query_string)
    #     token = query_params.get('auth', [None])[0]
    #     if token:
    #         return token

    #     return None
    
    