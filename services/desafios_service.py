from django.utils import timezone
from django.db.models import Q, F, Count, Sum, ExpressionWrapper, DurationField
from desafios.models import Desafio, UsuarioDesafio, TipoDesafio
from atividades.models import Atividade, AtividadeConcluidas
from atividades.models import SessaoPomodoro
from services import notificacao_service
from datetime import datetime, timedelta

from django.utils import timezone
from datetime import datetime, timedelta
from desafios.models import Desafio, UsuarioDesafio
from atividades.models import Atividade, AtividadeConcluidas, SessaoPomodoro
from services import notificacao_service


def verificar_desafios(usuario):
    agora = timezone.now()
    hoje = timezone.localdate()

    # Busca todos os desafios. Uma melhoria seria filtrar apenas os ativos.
    desafios = [d for d in Desafio.objects.all()]

    for desafio in desafios:
        # --- INÍCIO DA MUDANÇA NA LÓGICA ---

        # 1. Verifica se o usuário JÁ FOI RECOMPENSADO por este desafio alguma vez.
        #    Usar .exists() é mais eficiente do que .first() se você só precisa saber se algo existe.
        premiacao_existente = UsuarioDesafio.objects.filter(
            idusuario=usuario,
            iddesafio=desafio
        ).exists()

        # 2. Se uma premiação já existe, o desafio já foi completado e recompensado.
        #    Então, pulamos para o próximo desafio da lista.
        if premiacao_existente:
            continue

        # --- FIM DA MUDANÇA NA LÓGICA ---

        # 3. Se o código chegou até aqui, significa que o usuário NUNCA completou este desafio.
        #    Agora, vamos verificar se ele cumpriu os requisitos para ser recompensado PELA PRIMEIRA VEZ.

        # Define o intervalo de tempo para análise (a lógica para isso permanece a mesma)
        if desafio.tipo == 'diario':
            inicio = hoje
            fim = hoje
        elif desafio.tipo == 'semanal':
            inicio = hoje - timedelta(days=hoje.weekday())  # Segunda
            fim = inicio + timedelta(days=6)  # Domingo
        elif desafio.tipo == 'mensal':
            inicio = hoje.replace(day=1)
            proximo_mes = (inicio.replace(day=28) + timedelta(days=4)).replace(day=1)
            fim = proximo_mes - timedelta(days=1)
        else: # Para 'unico' ou outros tipos
            inicio = desafio.dtinicio.date()
            fim = desafio.dtfim.date()

        inicio_dt = timezone.make_aware(datetime.combine(inicio, datetime.min.time()))
        fim_dt = timezone.make_aware(datetime.combine(fim, datetime.max.time()))

        # Verifica se as condições foram atendidas dentro do período
        if desafio_foi_concluido(usuario, desafio, inicio_dt, fim_dt):
            # Se foram, entrega a premiação
            UsuarioDesafio.objects.create(
                idusuario=usuario,
                iddesafio=desafio,
                flsituacao=True,
                dtpremiacao=agora
            )

            # Lógica para adicionar XP e subir de nível
            nova_exp = usuario.expusuario + desafio.expdesafio
            while nova_exp >= 1000:
                usuario.nivelusuario += 1
                nova_exp -= 1000
            usuario.expusuario = nova_exp
            usuario.save()

            # Cria a notificação para o usuário
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
            hoje = timezone.localdate()
            innerjoin = AtividadeConcluidas.objects.filter(
                idusuario = usuario,
                dtconclusao__range = (inicio_dt, fim_dt),
            ).values('idatividade').distinct()
            atividades_no_dia = Atividade.objects.filter(
                idusuario = usuario,
                dtatividade__range = (inicio_dt, fim_dt),
                peso = 'muito_facil',
                idatividade__in = innerjoin
            ).count() >= p
            if not atividades_no_dia:
                return False
            return atividades_no_dia
            


        case 'streak_pomodoro_dias':
            dias_validos = 0
            for i in range(7):
                dia = inicio_dt + timedelta(days=i)
                qtd = SessaoPomodoro.objects.filter(
                    idusuario = usuario,
                    inicio__date = dia.date()
                ).count()
                if qtd >= 3:
                    dias_validos += 1
            return dias_validos >= p

        case 'recorrentes_concluidas':
            dias_validos = 0
            for i in range(7):
                dia = inicio_dt + timedelta(days=i)
                atividades = AtividadeConcluidas.objects.filter(
                    idusuario = usuario,
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

            return anterior > 0 and atual > anterior

        case 'percentual_concluido':
            total_desafios_mensais = Desafio.objects.filter(
                tipo='mensal',
                dtinicio__lte=fim_dt,
                dtfim__gte=inicio_dt
            ).count()

            if total_desafios_mensais == 0:
                return False

            desafios_concluidos_pelo_usuario = UsuarioDesafio.objects.filter(
                idusuario=usuario,
                iddesafio__tipo='mensal',
                dtpremiacao__range=(inicio_dt, fim_dt)
            ).count()

            if total_desafios_mensais == 0: 
                return False

            percentual_realizado = (desafios_concluidos_pelo_usuario / total_desafios_mensais) * 100
            return percentual_realizado >= p

        case 'desafios_concluidos':
            concluidos = UsuarioDesafio.objects.filter(
                idusuario=usuario,
                dtpremiacao__range=(inicio_dt, fim_dt)
            ).count()
            return concluidos >= p


    return False


def listar_desafios_ativos_nao_concluidos(usuario):
    hoje = timezone.localdate()
    concluidos_ids = []

    for ud in UsuarioDesafio.objects.filter(idusuario=usuario, flsituacao=True):
        dtpremiacao = ud.dtpremiacao.date() if hasattr(ud.dtpremiacao, 'date') else ud.dtpremiacao
        d = ud.iddesafio

        if d.tipo == 'diario' and dtpremiacao == hoje:
            concluidos_ids.append(d.iddesafio)
        elif d.tipo == 'semanal' and dtpremiacao.isocalendar()[1] == hoje.isocalendar()[1] and dtpremiacao.year == hoje.year:
            concluidos_ids.append(d.iddesafio)
        elif d.tipo == 'mensal' and dtpremiacao.month == hoje.month and dtpremiacao.year == hoje.year:
            concluidos_ids.append(d.iddesafio)
        elif d.tipo == 'unico':
            concluidos_ids.append(d.iddesafio)

    desafios_ativos = [d for d in Desafio.objects.all() if d.is_ativo()]
    

    return desafios_ativos, concluidos_ids
