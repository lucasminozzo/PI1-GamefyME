from conquistas.models import Conquista, UsuarioConquista
from atividades.models import AtividadeConcluidas, SessaoPomodoro
from services import notificacao_service

def verificar_conquistas(usuario):
    for c in Conquista.objects.all():
        if UsuarioConquista.objects.filter(usuario=usuario, conquista=c).exists():
            continue

        if _atingiu_criterio(usuario, c):
            UsuarioConquista.objects.create(usuario=usuario, conquista=c)
            usuario.expusuario += c.expconquista
            usuario.save()

            notificacao_service.criar_notificacao(
                usuario,
                f'🏅 Parabéns! Você desbloqueou a conquista "{c.nmconquista}" e ganhou {c.expconquista} XP!'
                'sucesso'
            )

def _atingiu_criterio(usuario, conquista):
    match conquista.criterio:
        case "qtd_atividades":
            return AtividadeConcluidas.objects.filter(usuario=usuario).count() >= conquista.parametro
        case "ciclos_pomodoro":
            return SessaoPomodoro.objects.filter(usuario=usuario).count() >= conquista.parametro
        case "dias_streak":
            from services.atividades_service import get_streak_data
            get_streak_data(usuario)
            return usuario.streak_atual >= conquista.parametro
    return False

def listar_conquistas_proximas(usuario):
    conquistas = Conquista.objects.all()
    conquistas_usuario = UsuarioConquista.objects.filter(idusuario=usuario).values_list('idconquista_id', flat=True)

    conquistas_proximas = [
        {
           'nome': c.nmconquista,
            'exp': c.expconquista,
            'concluida': False
        }
        for c in conquistas if c.idconquista not in conquistas_usuario
    ]
    return conquistas_proximas


