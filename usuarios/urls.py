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
    path('ajax/notificacoes/', views.ajax_todas_notificacoes, name='ajax_todas_notificacoes'),
    path('atualizar-config/', views.atualizar_config_usuario, name='atualizar_config_usuario'),
    path('atualizar_avatar/', views.atualizar_avatar, name='atualizar_avatar'),
    path('listar_usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('alterar_tipo/<int:idusuario>/', views.alterar_tipo_usuario, name='alterar_tipo_usuario'),
    path('alternar_situacao/<int:idusuario>/', views.alternar_situacao_usuario, name='alternar_situacao_usuario'),
    path('deletar_usuario/', views.deletar_usuario, name='deletar_usuario'),
]