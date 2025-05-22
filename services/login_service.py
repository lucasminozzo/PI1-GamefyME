from django.shortcuts import render
from usuarios.models import Usuario
from services import atividades_service

def is_usuario_logado(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return False
    
    return True

def get_usuario_logado(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(pk=usuario_id)
    atividades_service.verificar_streak_no_login(usuario)
    usuario.streak_data = atividades_service.get_streak_data(usuario)
    usuario.streak_atual = atividades_service.calcular_streak_atual(usuario)
    return usuario
