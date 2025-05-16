from django.shortcuts import render
from django.utils import timezone
from usuarios.models import Usuario
from atividades.models import Atividade, AtividadeConcluidas
from datetime import timedelta
from django.db.models import Q

def calcular_streak_atual(usuario):
    """
    Conta dias consecutivos (começando de hoje para trás) em que o usuário completou atividades.
    Se faltar um dia no meio, o streak é interrompido.
    """
    hoje = timezone.localdate()
    dias_seguidos = 0

    for i in range(0, 7):
        dia = hoje - timedelta(days=i)

        concluiu = AtividadeConcluidas.objects.filter(
            idusuario=usuario.idusuario,
            dtconclusao__date=dia
        ).exists()

        if concluiu:
            dias_seguidos += 1
        else:
            if i > 0:
                break
            else:
                return 0

    return dias_seguidos



def atualizar_streak(usuario):
    """
    Atualiza o streak do usuário baseado na última atividade concluída.
    """
    hoje = timezone.localdate()

    # Se já atualizou hoje, sai
    if usuario.ultima_atividade == hoje:
        return

    dias_desde_ultima = (hoje - usuario.ultima_atividade).days if usuario.ultima_atividade else None
    ontem = hoje - timedelta(days=1)

    concluiu_ontem = AtividadeConcluidas.objects.filter(
        idusuario=usuario.idusuario,
        dtconclusao__date=ontem
    ).exists()

    concluiu_hoje = AtividadeConcluidas.objects.filter(
        idusuario=usuario.idusuario,
        dtconclusao__date=hoje
    ).exists()

    if not concluiu_hoje:
        return

    if dias_desde_ultima == 1 and concluiu_ontem:
        usuario.streak_semanal += 1
    else:
        usuario.streak_semanal = 1

    usuario.streak_semanal = min(usuario.streak_semanal, 7)
    usuario.ultima_atividade = hoje
    usuario.save()
    return usuario.streak_semanal

def verificar_streak_no_login(usuario):
    """
    Zera o streak se ele não concluiu atividade hoje.
    Ajusta 'ultima_atividade' para a data do último registro.
    """
    hoje = timezone.localdate()

    concluiu_hoje = AtividadeConcluidas.objects.filter(
        idusuario=usuario.idusuario,
        dtconclusao__date=hoje
    ).exists()

    if not concluiu_hoje:
        usuario.streak_semanal = 0

        ultima = AtividadeConcluidas.objects.filter(
            idusuario=usuario.idusuario
        ).order_by('-dtconclusao').first()

        usuario.ultima_atividade = ultima.dtconclusao.date() if ultima else None
        usuario.save()

def get_atividades_do_dia(request):
    """
    Retorna as atividades realizadas hoje pelo usuário logado.
    """
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(pk=usuario_id)
    hoje = timezone.localdate()

    return Atividade.objects.filter(
        idusuario=usuario.idusuario,
        dtatividaderealizada=hoje,
        situacao='realizada'
    )
    
def get_streak_data(usuario):
    """
    Monta os dados de conclusão para os 7 dias da semana atual.
    Marca com 'quebrou' apenas o primeiro dia sem conclusão após sequência de dias concluídos.
    """
    hoje = timezone.localdate()
    domingo = hoje - timedelta(days=(hoje.weekday() + 1) % 7)
    dias_semana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab']
    streak_data = []

    em_streak = True
    congelado_mostrado = False

    for i in range(7):
        dia = domingo + timedelta(days=i)
        concluiu = AtividadeConcluidas.objects.filter(
            idusuario=usuario.idusuario,
            dtconclusao__date=dia
        ).exists()

        if concluiu:
            em_streak = True
            congelado_mostrado = False
            streak_data.append({
                'dia_semana': dias_semana[i],
                'data': dia,
                'concluiu': True,
                'quebrou': False
            })
        else:
            if em_streak and not congelado_mostrado:
                # primeira quebra do streak
                streak_data.append({
                    'dia_semana': dias_semana[i],
                    'data': dia,
                    'concluiu': False,
                    'quebrou': True
                })
                congelado_mostrado = True
            else:
                streak_data.append({
                    'dia_semana': dias_semana[i],
                    'data': dia,
                    'concluiu': False,
                    'quebrou': False
                })
            em_streak = False

    return streak_data

def calcular_experiencia(peso: str, tempo_estimado: int) -> int:
    exp_base = 50
    multiplicadores_peso = {
        'muito_facil': 1.0,
        'facil': 2.0,
        'medio': 3.0,
        'dificil': 4.0,
        'muito_dificil': 5.0
    }
    multiplicador_peso = multiplicadores_peso.get(peso, 1.0)

    if tempo_estimado <= 30:
        multiplicador_tempo = 1.0
    elif tempo_estimado <= 60:
        multiplicador_tempo = 1.5
    elif tempo_estimado <= 120:
        multiplicador_tempo = 2.0
    else:
        multiplicador_tempo = 2.5

    experiencia = round(exp_base * multiplicador_peso * multiplicador_tempo)
    return min(experiencia, 500)