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
    usuario.streak_data, usuario.streak_atual = atividades_service.get_streak_data(usuario)
    return usuario
