from conquistas.models import Conquista, UsuarioConquista
from atividades.models import AtividadeConcluidas, SessaoPomodoro
from services import notificacao_service
from services.atividades_service import get_streak_data, calcular_streak_criacao_atividades


def verificar_conquistas(usuario):
    conquistas = Conquista.objects.all()

    for conquista in conquistas:
        # Verifica se o usuário já possui essa conquista
        if UsuarioConquista.objects.filter(idusuario=usuario, idconquista=conquista).exists():
            continue

        if _atingiu_criterio(usuario, conquista):
            # Registra a conquista
            UsuarioConquista.objects.create(idusuario=usuario, idconquista=conquista)

            _premiar_usuario(usuario, conquista)

            notificacao_service.criar_notificacao(
                usuario,
                f'Parabéns! Você desbloqueou a conquista "{conquista.nmconquista}" e ganhou {conquista.expconquista} XP!',
                'sucesso'
            )


def _atingiu_criterio(usuario, conquista):
    """Define a lógica de desbloqueio baseado no nome da conquista (nmconquista)."""
    nome = conquista.nmconquista.upper()

    if nome == "ATIVIDADE CUMPRIDA":
        return AtividadeConcluidas.objects.filter(idusuario=usuario).count() >= 1

    elif nome == "PRODUTIVIDADE EM ALTA":
        return AtividadeConcluidas.objects.filter(idusuario=usuario).count() >= 10

    elif nome == "RECORRÊNCIA - DE NOVO!":
        return AtividadeConcluidas.objects.filter(
            idusuario=usuario,
            idatividade__recorrencia='recorrente'
        ).count() >= 5

    elif nome == "USUÁRIO HARDCORE":
        return AtividadeConcluidas.objects.filter(
            idusuario=usuario,
            idatividade__peso='dificil'
        ).count() >= 5

    elif nome == "PRIMEIRO CICLO":
        return SessaoPomodoro.objects.filter(idusuario=usuario).count() >= 1

    elif nome == "MARATONISTA POMODORO":
        return SessaoPomodoro.objects.filter(idusuario=usuario).count() >= 8

    elif nome == "DESAFIANTE AMADOR":
        from desafios.models import UsuarioDesafio
        return UsuarioDesafio.objects.filter(idusuario=usuario).count() >= 1

    elif nome == "DESAFIANTE MESTRE":
        from desafios.models import UsuarioDesafio
        return UsuarioDesafio.objects.filter(idusuario=usuario).count() >= 50

    elif nome == "CAMPEÃO SEMANAL":
        from desafios.models import UsuarioDesafio, Desafio
        return UsuarioDesafio.objects.filter(
            idusuario=usuario,
            iddesafio__tipo='semanal'
        ).count() >= Desafio.objects.filter(tipo='semanal').count()

    elif nome == "MISSÃO CUMPRIDA":
        from desafios.models import UsuarioDesafio
        return UsuarioDesafio.objects.filter(
            idusuario=usuario,
            iddesafio__tipo='mensal'
        ).exists()

    elif nome == "UM DIA APÓS O OUTRO":
        get_streak_data(usuario)
        return usuario.streak_atual >= 5

    elif nome == "RITUAL SEMANAL":
        streak = calcular_streak_criacao_atividades(usuario)
        return streak >= 7


    elif nome == "CONSISTÊNCIA INABALÁVEL":
        get_streak_data(usuario)
        return usuario.streak_atual >= 15

    return False


def _premiar_usuario(usuario, conquista):
    usuario.expusuario += conquista.expconquista
    while usuario.expusuario >= 1000:
        usuario.expusuario -= 1000
        usuario.nivelusuario += 1
    usuario.save()
