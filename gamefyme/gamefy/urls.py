from django.urls import path
from gamefy.views import my_view

urlpatterns = [
    path('', my_view)
]