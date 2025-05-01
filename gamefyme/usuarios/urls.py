from django.urls import path
from . import views

urlpatterns = [
    # Rotas de autenticação
    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('logout/', views.logout, name='logout'),
    path('main/', views.main, name='main'),
    path('esqueceu/',views.esqueceu, name='esqueceu'),
    path('nova_senha/<uidb64>/<token>/', views.nova_senha, name='nova_senha'),
]