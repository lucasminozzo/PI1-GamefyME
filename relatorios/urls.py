from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('atividades/pdf/', views.gerar_relatorio_atividades, name='atividades_pdf'),
]
