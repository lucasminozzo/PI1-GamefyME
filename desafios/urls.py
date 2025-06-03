from django.urls import path
from . import views

app_name = 'desafios'

urlpatterns = [
    path('', views.listar_desafios, name='listar'),
    path('cadastrar/', views.cadastrar_desafio, name='cadastrar'),
    path('editar/', views.editar, name='editar'),
]
