from django.shortcuts import render, redirect, get_object_or_404
from .forms import AtividadeForm
from django.utils import timezone
from services import login_service, atividades_service
from django.contrib import messages
from django.db import IntegrityError
from django.db import transaction
from .models import Atividade, SessaoPomodoro, AtividadeConcluidas
from usuarios.models import Notificacao
from datetime import date, datetime

def criar_notificacao(usuario, mensagem, tipo='info'):
    return Notificacao.objects.create(
        idusuario=usuario,
        dsmensagem=mensagem,
        fltipo=tipo
    )

def criar_atividade(request):
    if not login_service.is_usuario_logado(request):
        return redirect('usuarios:login')

    usuario = login_service.get_usuario_logado(request)

    if request.method == 'POST':
        form = AtividadeForm(request.POST)
        if form.is_valid():
            try:
                atividade = form.save(commit=False)
                atividade.idusuario = usuario
                atividade.dtatividade = timezone.now().date()
                atividade.situacao = 'ativa'

                atividade.expatividade = atividades_service.calcular_experiencia(
                    atividade.peso,
                    atividade.tpestimado
                )

                atividade.save()

                # Criar notificação para nova atividade
                criar_notificacao(
                    usuario=usuario,
                    mensagem=f'Nova atividade "{atividade.nmatividade}" criada! Boa sorte!',
                    tipo='info'
                )

                messages.success(request, f'Atividade "{atividade.nmatividade}" criada com sucesso!')
                return redirect('usuarios:main')
            except IntegrityError:
                messages.error(request, f'Já existe uma atividade chamada "{form.cleaned_data["nmatividade"]}". Por favor, escolha um nome diferente.')
    else:
        form = AtividadeForm()

    notificacoes = Notificacao.objects.filter(
        idusuario=usuario,
        flstatus=False
    ).order_by('-dtcriacao')[:5]

    notificacoes_nao_lidas = Notificacao.objects.filter(
        idusuario=usuario,
        flstatus=False
    ).count()

    return render(request, 'atividades/cadastro_atividade.html', {
        'form': form,
        'usuario': usuario,
        'notificacoes': notificacoes,
        'notificacoes_nao_lidas': notificacoes_nao_lidas
    })

@transaction.atomic
def realizar_atividade(request, idatividade):
    if not login_service.is_usuario_logado(request):
        return redirect('usuarios:login')

    usuario = login_service.get_usuario_logado(request)
    atividade = get_object_or_404(Atividade, pk=idatividade, idusuario=usuario)

    if atividade.situacao in [Atividade.Situacao.CANCELADA] or \
       (atividade.situacao == Atividade.Situacao.REALIZADA and atividade.recorrencia == Atividade.Recorrencia.UNICA):
        messages.error(request, "Esta atividade não pode ser alterada.")
        return redirect('usuarios:main')

    streak_data = atividades_service.get_streak_data(usuario)
    streak_atual = atividades_service.calcular_streak_atual(usuario)

    if request.method == 'POST':
        sid = transaction.savepoint()
        try:
            nivel_anterior = usuario.nivelusuario or 0
            exp_ganha = atividades_service.calcular_experiencia(atividade.peso, atividade.tpestimado)
            nova_exp = (usuario.expusuario or 0) + exp_ganha

            novo_nivel = nivel_anterior
            while nova_exp >= 1000:
                novo_nivel += 1
                nova_exp -= 1000

            atividade.situacao = Atividade.Situacao.ATIVA if atividade.recorrencia == Atividade.Recorrencia.RECORRENTE else Atividade.Situacao.REALIZADA
            atividade.dtatividaderealizada = timezone.now().date()

            atividade_concluida = AtividadeConcluidas(
                idusuario=usuario,
                idatividade=atividade,
                dtconclusao=timezone.now()
            )

            inicio = request.POST.get('inicio')
            fim = request.POST.get('fim')
            nrciclo = request.POST.get('nrciclo')

            sessao_pomodoro = None
            if inicio and fim:
                sessao_pomodoro = SessaoPomodoro(
                    idusuario=usuario,
                    idatividade=atividade,
                    inicio=inicio,
                    fim=fim,
                    nrciclo=int(nrciclo or 0)
                )

            try:
                streak_atual = atividades_service.atualizar_streak(usuario)
            except Exception:
                streak_atual = None

            usuario.nivelusuario = novo_nivel
            usuario.expusuario = nova_exp

            usuario.save()
            atividade.save()
            atividade_concluida.save()
            if sessao_pomodoro:
                sessao_pomodoro.save()

            criar_notificacao(usuario, f'Parabéns! Você completou a atividade "{atividade.nmatividade}" e ganhou {exp_ganha} XP!', 'sucesso')

            if novo_nivel > nivel_anterior:
                criar_notificacao(usuario, f'🎉 Incrível! Você alcançou o nível {novo_nivel}!', 'sucesso')

            if sessao_pomodoro and sessao_pomodoro.nrciclo > 0:
                criar_notificacao(usuario, f'Ótimo trabalho! Você completou {sessao_pomodoro.nrciclo} ciclos Pomodoro na atividade "{atividade.nmatividade}"', 'sucesso')

            if streak_atual and streak_atual > 1:
                criar_notificacao(usuario, f'🔥 Impressionante! Você manteve sua streak por {streak_atual} dias consecutivos!', 'sucesso')

            transaction.savepoint_commit(sid)

            messages.success(
                request,
                f'Atividade "{atividade.nmatividade}" concluída com sucesso! Você ganhou {exp_ganha} pontos de experiência!'
                + (f' Ciclos Pomodoro completos: {nrciclo}' if nrciclo else '')
            )
            return redirect('usuarios:main')

        except Exception as e:
            transaction.savepoint_rollback(sid)
            messages.error(request, f"Erro ao salvar a atividade: {str(e)}")

    notificacoes = Notificacao.objects.filter(
        idusuario=usuario,
        flstatus=False
    ).order_by('-dtcriacao')[:5]

    notificacoes_nao_lidas = notificacoes.count()

    return render(request, 'atividades/realizar_atividade.html', {
        'atividade': atividade,
        'usuario': usuario,
        'exibir_voltar': True,
        'notificacoes': notificacoes,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'streak_data': streak_data,
        'streak_atual': streak_atual,
        'today': date.today(),
    })

def editar_atividade(request, idatividade):
    if not login_service.is_usuario_logado(request):
        return redirect('usuarios:login')

    usuario = login_service.get_usuario_logado(request)
    atividade = get_object_or_404(Atividade, pk=idatividade, idusuario=usuario)

    if request.method == 'POST':
        form = AtividadeForm(request.POST, instance=atividade)
        if form.is_valid():
            try:
                atividade = form.save(commit=False)
                atividade.idusuario = usuario
                atividade.expatividade = atividades_service.calcular_experiencia(
                    atividade.peso,
                    atividade.tpestimado
                )
                atividade.save()

                # Notificação para edição de atividade
                criar_notificacao(
                    usuario=usuario,
                    mensagem=f'Atividade "{atividade.nmatividade}" foi atualizada com sucesso!',
                    tipo='info'
                )

                messages.success(request, f'Atividade "{atividade.nmatividade}" atualizada com sucesso!')
                return redirect('usuarios:main')
            except IntegrityError:
                messages.error(request, f'Já existe uma atividade chamada "{form.cleaned_data["nmatividade"]}". Por favor, escolha um nome diferente.')
    else:
        form = AtividadeForm(instance=atividade)

    notificacoes = Notificacao.objects.filter(
        idusuario=usuario,
        flstatus=False
    ).order_by('-dtcriacao')[:5]

    notificacoes_nao_lidas = Notificacao.objects.filter(
        idusuario=usuario,
        flstatus=False
    ).count()

    return render(request, 'atividades/editar_atividade.html', {
        'form': form,
        'usuario': usuario,
        'editar': True,
        'atividade': atividade,
        'notificacoes': notificacoes,
        'notificacoes_nao_lidas': notificacoes_nao_lidas
    })

def remover_atividade(request, idatividade):
    if not login_service.is_usuario_logado(request):
        return redirect('usuarios:login')

    usuario = login_service.get_usuario_logado(request)
    atividade = get_object_or_404(Atividade, pk=idatividade, idusuario=usuario)

    if atividade.situacao == Atividade.Situacao.CANCELADA:
        messages.error(request, "Esta atividade já está cancelada.")
        return redirect('usuarios:main')

    try:
        atividade.situacao = Atividade.Situacao.CANCELADA
        atividade.save()

        criar_notificacao(
            usuario=usuario,
            mensagem=f'Atividade "{atividade.nmatividade}" foi removida.',
            tipo='aviso'
        )

        messages.success(request, "Atividade removida com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao remover a atividade: {str(e)}")

    return redirect('usuarios:main')
