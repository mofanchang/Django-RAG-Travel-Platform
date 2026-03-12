from django.urls import path
from .views import chat_api, rebuild_rag_index

urlpatterns = [
    path("chat/", chat_api, name="chat_api"),
    path("rebuild/", rebuild_rag_index, name="rebuild_rag_index"),
]
