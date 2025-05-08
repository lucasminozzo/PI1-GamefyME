from django.shortcuts import render
from usuarios.models import Usuario
from atividades.models import Atividade, AtividadeConcluidas
from datetime import date, timedelta
from django.db.models import Q

def get_atividades_do_dia(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(pk=usuario_id)
    hoje = date.today()

    atividades_concluidas = AtividadeConcluidas.objects.filter(
        idusuario=usuario.idusuario,
        dtconclusao=hoje
    ).values_list('idatividade', flat=True)

    return Atividade.objects.filter(idatividade__in=atividades_concluidas)

def atualizar_streak(usuario):
    """Atualiza o streak do usuário baseado na última atividade concluída"""
    hoje = date.today()

    if usuario.ultima_atividade == hoje:
        return

    if usuario.ultima_atividade:
        dias_desde_ultima = (hoje - usuario.ultima_atividade).days
    else:
        dias_desde_ultima = None

    ontem = hoje - timedelta(days=1)
    concluiu_ontem = AtividadeConcluidas.objects.filter(
        idusuario=usuario.idusuario,
        dtconclusao=ontem
    ).exists()

    concluiu_hoje = AtividadeConcluidas.objects.filter(
        idusuario=usuario.idusuario,
        dtconclusao=hoje
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
    
def verificar_streak_no_login(usuario):
    hoje = date.today()

    concluiu_hoje = AtividadeConcluidas.objects.filter(
        idusuario=usuario.idusuario,
        dtconclusao=hoje
    ).exists()

    if not concluiu_hoje:
        usuario.streak_semanal = 0

        ultima_atividade_obj = AtividadeConcluidas.objects.filter(
            idusuario=usuario.idusuario
        ).order_by('-dtconclusao').first()

        if ultima_atividade_obj:
            usuario.ultima_atividade = ultima_atividade_obj.dtconclusao
        else:
            usuario.ultima_atividade = None

        usuario.save()

def calcular_experiencia(peso: str, tempo_estimado: int) -> int:
    """
    Calcula a experiência baseada no peso e tempo estimado da atividade

    Args:
        peso (str): Peso da atividade (muito_facil, facil, medio, dificil, muito_dificil)
        tempo_estimado (int): Tempo estimado em minutos

    Returns:
        int: Quantidade de experiência (máximo 500)
    """
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

def get_atividades_do_dia(request):
    """Retorna as atividades realizadas hoje"""
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(pk=usuario_id)
    hoje = date.today()

    return Atividade.objects.filter(
        idusuario=usuario.idusuario,
        dtatividaderealizada=hoje,
        situacao='realizada'
    ).all()
    
def get_streak_data(usuario):
    hoje = date.today()
    streak_data = []

    dias_semana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab']

    domingo = hoje - timedelta(days=hoje.weekday() + 1 if hoje.weekday() < 6 else 0)

    for i in range(7):
        dia = domingo + timedelta(days=i)
        concluiu = AtividadeConcluidas.objects.filter(
            idusuario=usuario.idusuario,
            dtconclusao=dia
        ).exists()

        streak_data.append({
            'dia_semana': dias_semana[i],
            'data': dia,
            'concluiu': concluiu
        })

    return streak_data