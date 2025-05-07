from django.shortcuts import render, redirect, get_object_or_404
from .forms import AtividadeForm
from django.utils import timezone
from services import login_service, atividades_service
from django.contrib import messages
from django.db import IntegrityError
from django.db import transaction
from django.utils import timezone
from .models import Atividade, SessaoPomodoro, AtividadeConcluidas
from usuarios.models import Notificacao

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

    return render(request, 'atividades/cadastro_atividade.html', {
        'form': form,
        'usuario': usuario
    })

@transaction.atomic
def realizar_atividade(request, idatividade):
    if not login_service.is_usuario_logado(request):
        return redirect('usuarios:login')

    usuario = login_service.get_usuario_logado(request)
    atividade = get_object_or_404(Atividade, pk=idatividade, idusuario=usuario)

    # Verificações iniciais
    if atividade.situacao in [Atividade.Situacao.CANCELADA]:
        messages.error(request, "Esta atividade não pode ser alterada.")
        return redirect('usuarios:main')

    elif atividade.situacao in [Atividade.Situacao.REALIZADA] and atividade.recorrencia in [Atividade.Recorrencia.UNICA]:
        messages.error(request, "Esta atividade não pode ser alterada.")
        return redirect('usuarios:main')

    if request.method == 'POST':
        sid = transaction.savepoint()

        try:
            nivel_anterior = usuario.nivelusuario or 0
            exp_ganha = atividades_service.calcular_experiencia(
                atividade.peso,
                atividade.tpestimado
            )
            nova_exp = (usuario.expusuario or 0) + exp_ganha

            novo_nivel = (usuario.nivelusuario or 0)
            while nova_exp >= 1000:
                novo_nivel += 1
                nova_exp -= 1000

            if atividade.recorrencia in [Atividade.Recorrencia.RECORRENTE]:
                atividade.situacao = Atividade.Situacao.ATIVA
            else:
                atividade.situacao = Atividade.Situacao.REALIZADA
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

            criar_notificacao(
                usuario=usuario,
                mensagem=f'Parabéns! Você completou a atividade "{atividade.nmatividade}" e ganhou {exp_ganha} XP!',
                tipo='sucesso'
            )

            if novo_nivel > nivel_anterior:
                criar_notificacao(
                    usuario=usuario,
                    mensagem=f'🎉 Incrível! Você alcançou o nível {novo_nivel}!',
                    tipo='sucesso'
                )

            if sessao_pomodoro and nrciclo and int(nrciclo) > 0:
                criar_notificacao(
                    usuario=usuario,
                    mensagem=f'Ótimo trabalho! Você completou {nrciclo} ciclos Pomodoro na atividade "{atividade.nmatividade}"',
                    tipo='sucesso'
                )

            if streak_atual and streak_atual > 1:
                criar_notificacao(
                    usuario=usuario,
                    mensagem=f'🔥 Impressionante! Você manteve sua streak por {streak_atual} dias consecutivos!',
                    tipo='sucesso'
                )

            transaction.savepoint_commit(sid)

            messages.success(
                request,
                f'Atividade "{atividade.nmatividade}" concluída com sucesso! ' +
                f'Você ganhou {exp_ganha} pontos de experiência!' +
                (f' Ciclos Pomodoro completos: {nrciclo}' if nrciclo else '')
            )
            return redirect('usuarios:main')

        except Exception as e:
            transaction.savepoint_rollback(sid)
            messages.error(request, f"Erro ao salvar a atividade: {str(e)}")
            return render(request, 'atividades/realizar_atividade.html', {
                'atividade': atividade,
                'usuario': usuario
            })

    return render(request, 'atividades/realizar_atividade.html', {
        'atividade': atividade,
        'usuario': usuario,
        'exibir_voltar': True,
    })
    if not login_service.is_usuario_logado(request):
        return redirect('usuarios:login')

    usuario = login_service.get_usuario_logado(request)
    atividade = get_object_or_404(Atividade, pk=idatividade, idusuario=usuario)

    if atividade.situacao in [Atividade.Situacao.CANCELADA]:
        messages.error(request, "Esta atividade não pode ser alterada.")
        return redirect('usuarios:main')

    elif atividade.situacao in [Atividade.Situacao.REALIZADA] and atividade.recorrencia in [Atividade.Recorrencia.UNICA]:
        messages.error(request, "Esta atividade não pode ser alterada.")
        return redirect('usuarios:main')

    if request.method == 'POST':
        try:
            nivel_anterior = usuario.nivelusuario or 0
            if atividade.recorrencia in [Atividade.Recorrencia.RECORRENTE]:
                atividade.situacao = Atividade.Situacao.ATIVA
            else:
                atividade.situacao = Atividade.Situacao.REALIZADA

            atividade.dtatividaderealizada = timezone.now().date()

            exp_ganha = atividades_service.calcular_experiencia(
                atividade.peso,
                atividade.tpestimado
            )
            nova_exp = (usuario.expusuario or 0) + exp_ganha

            while nova_exp >= 1000:
                usuario.nivelusuario = (usuario.nivelusuario or 0) + 1
                nova_exp -= 1000

            usuario.expusuario = nova_exp

            atividade.save()
            usuario.save()

            criar_notificacao(
                usuario=usuario,
                mensagem=f'Parabéns! Você completou a atividade "{atividade.nmatividade}" e ganhou {exp_ganha} XP!',
                tipo='sucesso'
            )

            if usuario.nivelusuario is not None and nivel_anterior is not None:
                if usuario.nivelusuario > nivel_anterior:
                    criar_notificacao(
                        usuario=usuario,
                        mensagem=f'🎉 Incrível! Você alcançou o nível {usuario.nivelusuario}!',
                        tipo='sucesso'
                    )

            AtividadeConcluidas.objects.create(
                idusuario=usuario,
                idatividade=atividade,
                dtconclusao=timezone.now()
            )

            inicio = request.POST.get('inicio')
            fim = request.POST.get('fim')
            nrciclo = request.POST.get('nrciclo')

            if inicio and fim:
                try:
                    SessaoPomodoro.objects.create(
                        idusuario=usuario,
                        idatividade=atividade,
                        inicio=inicio,
                        fim=fim,
                        nrciclo=int(nrciclo or 0)
                    )

                    if nrciclo and int(nrciclo) > 0:
                        criar_notificacao(
                            usuario=usuario,
                            mensagem=f'Ótimo trabalho! Você completou {nrciclo} ciclos Pomodoro na atividade "{atividade.nmatividade}"',
                            tipo='sucesso'
                        )
                except Exception as e:
                    messages.warning(
                        request,
                        f"Atividade concluída, mas houve um erro ao salvar a sessão Pomodoro: {str(e)}"
                    )

            streak_atual = atividades_service.atualizar_streak(usuario)
            if streak_atual is not None and streak_atual > 1:
                criar_notificacao(
                    usuario=usuario,
                    mensagem=f'🔥 Impressionante! Você manteve sua streak por {streak_atual} dias consecutivos!',
                    tipo='sucesso'
                )

            messages.success(
                request,
                f'Atividade "{atividade.nmatividade}" concluída com sucesso! ' +
                f'Você ganhou {exp_ganha} pontos de experiência!' +
                (f' Ciclos Pomodoro completos: {nrciclo}' if nrciclo else '')
            )
            return redirect('usuarios:main')

        except Exception as e:
            messages.error(request, f"Erro ao salvar a atividade: {str(e)}")
            return render(request, 'atividades/realizar_atividade.html', {
                'atividade': atividade,
                'usuario': usuario
            })

    return render(request, 'atividades/realizar_atividade.html', {
        'atividade': atividade,
        'usuario': usuario,
        'exibir_voltar': True,
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

    return render(request, 'atividades/editar_atividade.html', {
        'form': form,
        'usuario': usuario,
        'editar': True,
        'atividade': atividade,
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

        # Notificação para remoção de atividade
        criar_notificacao(
            usuario=usuario,
            mensagem=f'Atividade "{atividade.nmatividade}" foi removida.',
            tipo='aviso'
        )

        messages.success(request, "Atividade removida com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao remover a atividade: {str(e)}")

    return redirect('usuarios:main')
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

        # Notificação para remoção de atividade
        criar_notificacao(
            usuario=usuario,
            mensagem=f'Atividade "{atividade.nmatividade}" foi removida.',
            tipo='aviso'
        )

        messages.success(request, "Atividade removida com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao remover a atividade: {str(e)}")

    return redirect('usuarios:main')
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
        messages.success(request, "Atividade removida com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao remover a atividade: {str(e)}")

    return redirect('usuarios:main')