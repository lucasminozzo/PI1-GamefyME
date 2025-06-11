from django.urls import path
from . import views

app_name = 'atividades'

urlpatterns = [
    path('nova/', views.criar_atividade, name='atividade'),
    path('realizar_atividade/<int:idatividade>/', views.realizar_atividade, name='realizar_atividade'),
    path('remover_atividade/<int:idatividade>/', views.remover_atividade, name='remover_atividade'),
    path('editar_atividade/<int:idatividade>/', views.editar_atividade, name='editar_atividade'),
    path('listar/', views.listar_atividades, name='listar_atividades'),
]