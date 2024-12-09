from django.urls import path
from .views import desktop_5

urlpatterns = [
    path('desktop_5/', desktop_5, name='desktop-5')
]