from django.shortcuts import render
from usuarios.models import Usuario
from atividades.models import Atividade
from datetime import date, timedelta

def get_atividade(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(pk=usuario_id)
    atividades = Atividade.objects.filter(idusuario=usuario.idusuario).all()
    return atividades

def atualizar_streak(usuario):
    hoje = date.today()
    ontem = hoje - timedelta(days=1)
    
    if usuario.ultima_atividade == hoje:
        return

    if usuario.ultima_atividade == ontem:
        usuario.streak_semanal += 1
    else:
        usuario.streak_semanal = 1

    usuario.ultima_atividade = hoje
    usuario.save()

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