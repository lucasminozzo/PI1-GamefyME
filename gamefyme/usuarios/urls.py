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
    path('marcar_notificacao_lida/<int:notificacao_id>/', views.marcar_notificacao_lida, name='marcar_notificacao_lida'),
    path('marcar_todas_lidas/', views.marcar_todas_lidas, name='marcar_todas_lidas'),
    path('config_usuario/', views.config_usuario, name='config_usuario'),
    path('atualizar_avatar/', views.atualizar_avatar, name='atualizar_avatar'),
]