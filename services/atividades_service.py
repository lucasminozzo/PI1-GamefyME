from django.utils import timezone
from atividades.models import AtividadeConcluidas
from datetime import timedelta

def calcular_experiencia(peso: str, tempo_estimado: int) -> int: ##     RN 05 - RF 03 - A experiência que o usuário receberá após cada atividade 
                                                                 ## não poderá ultrapassar de 500 e tem um mínimo de 50.
                                                                 ## Caso o cálculo feito ultrapasse esse valor máximo, o sistema retornará o limite de 500.

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
    hoje = timezone.localdate()
    segunda = hoje - timedelta(days=hoje.weekday())
    dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']
    streak_data = []

    datas_semana = [segunda + timedelta(days=i) for i in range(7)]

    concluidas_qs = AtividadeConcluidas.objects.filter(
        idusuario=usuario.idusuario,
        dtconclusao__date__range=(segunda, segunda + timedelta(days=6))
    )

    concluidas = set(concluidas_qs.values_list('dtconclusao__date', flat=True))

    # Se o usuário não tem nenhuma atividade concluída na semana
    if not concluidas:
        for i, dia in enumerate(datas_semana):
            streak_data.append({
                'dia_semana': dias_semana[i],
                'data': dia,
                'concluiu': False,
                'quebrou': False
            })
        return streak_data, 0

    dias_seguidos = 0
    esperando_quebra = True
    congelado_mostrado = False

    for i, dia in enumerate(datas_semana):
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

    return streak_data, dias_seguidos
