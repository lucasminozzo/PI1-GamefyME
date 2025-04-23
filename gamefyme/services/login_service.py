from django.shortcuts import render
from usuarios.models import Usuario

def is_usuario_logado(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return False
    
    return True

def get_usuario_logado(request):
    usuario_id = request.session.get('usuario_id')
    return Usuario.objects.get(pk=usuario_id)

def get_nome_usuario_logado(request):
    return request.session.get('usuario_nome')