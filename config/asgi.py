import os
import sys
from pathlib import Path
from django.core.asgi import get_asgi_application
from config.settings.conf import app_config

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(BASE_DIR / "src"))

DJANGO_SETTINGS_MODULE = app_config.DJANGO_SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)

django_application = get_asgi_application()


# Import websocket application here, so apps from django_application are loaded first
from config.websocket import websocket_application  # noqa isort:skip
async def application(scope, receive, send):
    if scope["type"] == "http":
        await django_application(scope, receive, send)
    elif scope["type"] == "websocket":
        await websocket_application(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")


from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import OriginValidator

from src.routing import websocket_urlpatterns
from src.websocket.middleware import CustomerIDMiddleware

application = ProtocolTypeRouter(
    {
        "http": django_application,
        "websocket": OriginValidator(
            CustomerIDMiddleware(URLRouter(websocket_urlpatterns)),
            ["*"] 
        ),
    }
)
