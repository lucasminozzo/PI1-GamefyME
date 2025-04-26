from django.urls import path
from . import views

app_name = 'atividades'

urlpatterns = [
    path('nova/', views.criar_atividade, name='atividade'),
    path('realizar/<int:idatividade>/', views.realizar_atividade, name='realizar_atividade'),
]