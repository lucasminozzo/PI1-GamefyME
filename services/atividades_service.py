from django.utils import timezone
from atividades.models import AtividadeConcluidas
from datetime import timedelta

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

def get_streak_data(usuario):
    """
    Exibe a semana atual de segunda a domingo.
    Marca:
    - fogo-ativo: dias com atividade e streak ainda válido
    - fogo-congelado: primeira falha (até hoje)
    - fogo-inativo: dias sem atividade fora do streak
    - dias futuros: ignorados como quebra
    """
    hoje = timezone.localdate()
    segunda = hoje - timedelta(days=hoje.weekday())
    dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']
    streak_data = []

    dias_seguidos = 0
    esperando_quebra = True
    congelado_mostrado = False

    datas_semana = [segunda + timedelta(days=i) for i in range(7)]
    concluidas = set(
        AtividadeConcluidas.objects.filter(
            idusuario=usuario.idusuario,
            dtconclusao__date__range=(segunda, segunda + timedelta(days=6))
        ).values_list('dtconclusao__date', flat=True)
    )

    for i, dia in enumerate(datas_semana):

        # Dias futuros são ignorados para quebra
        if dia > hoje:
            streak_data.append({
                'dia_semana': dias_semana[i],
                'data': dia,
                'concluiu': False,
                'quebrou': False
            })
            continue

        concluiu = dia in concluidas

        if concluiu:
            if esperando_quebra:
                dias_seguidos += 1
            else:
                dias_seguidos = 1
                esperando_quebra = True

            streak_data.append({
                'dia_semana': dias_semana[i],
                'data': dia,
                'concluiu': True,
                'quebrou': False
            })
        else:
            if esperando_quebra and not congelado_mostrado:
                congelado_mostrado = True
                esperando_quebra = False
                streak_data.append({
                    'dia_semana': dias_semana[i],
                    'data': dia,
                    'concluiu': False,
                    'quebrou': True
                })
            elif esperando_quebra:
                esperando_quebra = False
                streak_data.append({
                    'dia_semana': dias_semana[i],
                    'data': dia,
                    'concluiu': False,
                    'quebrou': True
                })
            else:
                streak_data.append({
                    'dia_semana': dias_semana[i],
                    'data': dia,
                    'concluiu': False,
                    'quebrou': False
                })

    usuario.streak_atual = dias_seguidos
    return streak_data
