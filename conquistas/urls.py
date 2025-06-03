from django.urls import path
from . import views

app_name = 'conquistas'

urlpatterns = [
    path('', views.listar_conquistas, name='listar'),
    path('cadastrar/', views.cadastrar_conquista, name='cadastrar'),
]
