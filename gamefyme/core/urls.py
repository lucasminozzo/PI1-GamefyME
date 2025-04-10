from django.urls import path
from core.views import my_view

urlpatterns = [
    path('', my_view)
]