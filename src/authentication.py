from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _
from knox.auth import TokenAuthentication
from rest_framework.authentication import (
    get_authorization_header,
)
from knox.settings import knox_settings

class CustomAuthenticator(TokenAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        prefix = knox_settings.AUTH_HEADER_PREFIX.encode()

        if not auth:
            return None
        if auth[0].lower() != prefix.lower():
            # Authorization header is possibly for another backend
            return None
        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. '
                    'Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)
        
        user, auth_token = self.authenticate_credentials(auth[1])
        return (user, auth_token)
