from django.urls import path
from api import consumers


websocket_urlpatterns = [
    path('trainer/chat/<int:trainer_id>/<int:thread_id>/', consumers.ChatConsumer.as_asgi()),
    path('user/chat/<int:trainer_id>/<int:thread_id>/', consumers.ChatConsumer.as_asgi())
]
