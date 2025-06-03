from conquistas.models import Conquista, UsuarioConquista
from atividades.models import AtividadeConcluidas, SessaoPomodoro
from django.utils import timezone
from services import notificacao_service
from datetime import timedelta

def verificar_conquistas(usuario):
    for c in Conquista.objects.all():
        if UsuarioConquista.objects.filter(usuario=usuario, conquista=c).exists():
            continue

        if _atingiu_criterio(usuario, c):
            UsuarioConquista.objects.create(usuario=usuario, conquista=c)
            usuario.expusuario += c.recompensa_xp
            usuario.save()

            notificacao_service.criar_notificacao(
                usuario,
                f'🏅 Parabéns! Você desbloqueou a conquista "{c.nome}" e ganhou {c.recompensa_xp} XP!',
                'sucesso'
            )

def _atingiu_criterio(usuario, conquista):
    hoje = timezone.localdate()
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
            'nome': c.nome,
            'exp': c.recompensa_xp,
            'concluida': False
        }
        for c in conquistas if c.id not in conquistas_usuario
    ]
    return conquistas_proximas


