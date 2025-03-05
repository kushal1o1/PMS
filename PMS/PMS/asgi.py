import os

# Update with your app name
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')

django_application = get_asgi_application()
from userhome.routing import websocket_urlpatterns  # noqa isort:skip 


application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles HTTP requests
    "websocket": AuthMiddlewareStack(  # Handles WebSocket requests
        URLRouter(websocket_urlpatterns)
    ),
})
