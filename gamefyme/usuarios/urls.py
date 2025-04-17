from django.urls import path
from . import views

urlpatterns = [
    # Rotas de autenticação
    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('logout/', views.logout, name='logout'),
    path('main/', views.main, name='main'),
]