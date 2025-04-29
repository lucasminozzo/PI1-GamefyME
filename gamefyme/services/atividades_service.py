from django.shortcuts import render
from usuarios.models import Usuario
from atividades.models import Atividade
from datetime import date, timedelta
from django.db.models import Q

def get_atividade(request):
    """Retorna todas as atividades do usuário"""
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(pk=usuario_id)
    return Atividade.objects.filter(idusuario=usuario.idusuario).all()

def get_atividades_separadas(request):
    """Retorna as atividades separadas por tipo e não realizadas"""
    atividades = get_atividade(request)

    return {
        'unicas': [a for a in atividades if a.recorrencia == 'unica' and a.situacao != 'realizada'],
        'recorrentes': [a for a in atividades if a.recorrencia == 'recorrente' and a.situacao != 'realizada']
    }

def atualizar_streak(usuario):
    """Atualiza o streak do usuário baseado na última atividade"""
    hoje = date.today()

    if usuario.ultima_atividade == hoje:
        return

    if usuario.ultima_atividade:
        dias_desde_ultima = (hoje - usuario.ultima_atividade).days
    else:
        dias_desde_ultima = None

    if dias_desde_ultima == 1:
        usuario.streak_semanal += 1
    elif dias_desde_ultima is None or dias_desde_ultima > 1:
        usuario.streak_semanal = 1

    usuario.streak_semanal = min(usuario.streak_semanal, 7)

    usuario.ultima_atividade = hoje
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