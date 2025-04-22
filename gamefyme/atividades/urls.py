from django.urls import path
from . import views

app_name = 'atividades'

urlpatterns = [
    path('nova/', views.criar_atividade, name='atividade'),
    # path('lista/', views.lista_atividades, name='lista'),  # Exemplo para listar
]