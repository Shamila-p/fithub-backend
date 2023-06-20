import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fithub.settings')
django.setup()

# Define your Django application
django_application = get_asgi_application()

# Define your Channels application
from .routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        'http': django_application,
        'websocket': URLRouter(websocket_urlpatterns),
    }
)