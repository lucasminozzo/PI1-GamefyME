from django.utils import timezone
from desafios.models import Desafio, UsuarioDesafio
from atividades.models import Atividade, AtividadeConcluidas
from atividades.models import SessaoPomodoro
from services import notificacao_service
from datetime import datetime, timedelta



def verificar_desafios(usuario):
    agora = timezone.now()
    hoje = timezone.localdate()

    desafios = [d for d in Desafio.objects.all() if d.is_ativo()]

    for desafio in desafios:
        # já premiado
        if UsuarioDesafio.objects.filter(idusuario=usuario, iddesafio=desafio).exists():
            continue

        tipo = desafio.tipo
        valido = False

        # intervalo de verificação
        if tipo == 'diario':
            inicio = hoje
        elif tipo == 'semanal':
            inicio = hoje - timedelta(days=hoje.weekday())
        else:
            inicio = hoje.replace(day=1)

        # normaliza datas
        inicio_dt = timezone.make_aware(datetime.combine(inicio, timezone.datetime.min.time()))
        fim_dt = timezone.make_aware(datetime.combine(inicio, timezone.datetime.max.time()))

        valido = desafio_foi_concluido(usuario, desafio, inicio_dt, fim_dt)

        # Aqui você pode aplicar regras específicas por `desafio.iddesafio` se desejar mais precisão

        if valido:
            UsuarioDesafio.objects.create(
                idusuario=usuario,
                iddesafio=desafio,
                flsituacao=True,
                dtpremiacao=agora
            )

            nova_exp = usuario.expusuario + desafio.expdesafio
            while nova_exp >= 1000:
                usuario.nivelusuario += 1
                nova_exp -= 1000
            usuario.expusuario = nova_exp
            usuario.save()

            notificacao_service.criar_notificacao(
                usuario,
                f'Você concluiu o desafio "{desafio.nmdesafio}" e ganhou {desafio.expdesafio} XP!',
                'sucesso'
            )


def desafio_foi_concluido(usuario, desafio, inicio_dt, fim_dt):
    p = desafio.parametro or 1
    logica = desafio.tipo_logica

    match logica:
        case 'pomodoro':
            return SessaoPomodoro.objects.filter(
                idusuario=usuario,
                inicio__range=(inicio_dt, fim_dt)
            ).count() >= p

        case 'todas_atividades':
            return not Atividade.objects.filter(
                idusuario=usuario,
                dtatividade__range=(inicio_dt, fim_dt),
                situacao='ativa'
            ).exists()

        case 'atividades_criadas':
            return Atividade.objects.filter(
                idusuario=usuario,
                dtatividade__range=(inicio_dt, fim_dt)
            ).count() >= p

        case 'min_dificeis':
            return AtividadeConcluidas.objects.filter(
                idusuario=usuario,
                dtconclusao__range=(inicio_dt, fim_dt),
                idatividade__peso='dificil'
            ).count() >= p

        case 'min_atividades_por_peso':
            return AtividadeConcluidas.objects.filter(
                idusuario=usuario,
                dtconclusao__range=(inicio_dt, fim_dt),
                idatividade__peso__in=['medio', 'facil']
            ).count() >= p

        case 'todas_muito_faceis':
            return not Atividade.objects.filter(
                idusuario=usuario,
                dtatividade__range=(inicio_dt, fim_dt),
                peso='muito_facil',
                situacao='ativa'
            ).exists()

        case 'streak_pomodoro_dias':
            dias_validos = 0
            for i in range(7):
                dia = inicio_dt + timedelta(days=i)
                qtd = SessaoPomodoro.objects.filter(
                    idusuario=usuario,
                    inicio__date=dia.date()
                ).count()
                if qtd >= 3:
                    dias_validos += 1
            return dias_validos >= p

        case 'recorrentes_concluidas':
            dias_validos = 0
            for i in range(7):
                dia = inicio_dt + timedelta(days=i)
                atividades = AtividadeConcluidas.objects.filter(
                    idusuario=usuario,
                    dtconclusao__date=dia.date(),
                    idatividade__recorrencia='recorrente'
                ).exists()
                if atividades:
                    dias_validos += 1
            return dias_validos >= p

        case 'atividades_concluidas':
            return AtividadeConcluidas.objects.filter(
                idusuario=usuario,
                dtconclusao__range=(inicio_dt, fim_dt)
            ).count() >= p

        case 'tempo_total_pomodoro':
            sessoes = SessaoPomodoro.objects.filter(
                idusuario=usuario,
                inicio__range=(inicio_dt, fim_dt),
                fim__isnull=False
            )
            total_min = sum([(s.fim - s.inicio).total_seconds() / 60 for s in sessoes])
            return total_min >= p

        case 'streak_diario':
            hoje = timezone.now().date()
            dias_validos = 0
            for i in range(p):
                dia = hoje - timedelta(days=i)
                atividades = AtividadeConcluidas.objects.filter(
                    idusuario=usuario,
                    dtconclusao__date=dia
                ).exists()
                if atividades:
                    dias_validos += 1
                else:
                    break
            return dias_validos == p

        case 'melhora_pomodoro_media':
            # Simplificado: se neste mês usou mais sessões que no anterior
            hoje = timezone.now()
            inicio_mes = hoje.replace(day=1)
            inicio_mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)

            atual = SessaoPomodoro.objects.filter(
                idusuario=usuario,
                inicio__gte=inicio_mes
            ).count()

            anterior = SessaoPomodoro.objects.filter(
                idusuario=usuario,
                inicio__range=(inicio_mes_anterior, inicio_mes)
            ).count()

            return atual > anterior

        case 'percentual_concluido':
            total = Atividade.objects.filter(
                idusuario=usuario,
                dtatividade__range=(inicio_dt, fim_dt)
            ).count()
            concluidas = AtividadeConcluidas.objects.filter(
                idusuario=usuario,
                dtconclusao__range=(inicio_dt, fim_dt)
            ).count()
            if total == 0:
                return False
            return (concluidas / total * 100) >= p

    return False