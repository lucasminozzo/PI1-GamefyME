from django.shortcuts import render, redirect, get_object_or_404
from .forms import AtividadeForm
from django.utils import timezone
from services import login_service, atividades_service
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import json
from django.db import transaction
from .models import Atividade, SessaoPomodoro, Usuario

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
                atividade.situacao = 'iniciada'

                atividade.expatividade = atividades_service.calcular_experiencia(
                    atividade.peso,
                    atividade.tpestimado
                )

                atividade.save()

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
    
    if atividade.situacao in [Atividade.Situacao.CANCELADA, Atividade.Situacao.REALIZADA]:
        messages.error(request, "Esta atividade não pode ser removida.")
        return redirect('usuarios:main')

    if request.method == 'POST':
        try:
            atividade.situacao = Atividade.Situacao.REALIZADA
            atividade.dtatividaderealizada = timezone.now().date()

            exp_ganha = atividades_service.calcular_experiencia(
                atividade.peso,
                atividade.tpestimado
            )
            nova_exp = usuario.expusuario + exp_ganha

            while nova_exp >= 1000:
                usuario.nivelusuario += 1
                nova_exp -= 1000

            usuario.expusuario = nova_exp

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
                except Exception as e:
                    messages.warning(
                        request,
                        f"Atividade concluída, mas houve um erro ao salvar a sessão Pomodoro: {str(e)}"
                    )

            atividade.save()
            usuario.save()

            atividades_service.atualizar_streak(usuario)

            messages.success(
                request,
                f'Atividade "{atividade.nmatividade}" concluída com sucesso! ' +
                f'Você ganhou {exp_ganha} pontos de experiência!' +
                (f' Ciclos Pomodoro completados: {nrciclo}' if nrciclo else '')
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
        'usuario': usuario
    })
    
def remover_atividade(request, idatividade):
    if not login_service.is_usuario_logado(request):
        return redirect('usuarios:login')

    usuario = login_service.get_usuario_logado(request)
    atividade = get_object_or_404(Atividade, pk=idatividade, idusuario=usuario)

    if atividade.situacao in [Atividade.Situacao.CANCELADA, Atividade.Situacao.REALIZADA]:
        messages.error(request, "Esta atividade não pode ser removida.")
        return redirect('usuarios:main')

    if request.method == 'POST':
        try:
            atividade.situacao = Atividade.Situacao.CANCELADA
            atividade.save()

            messages.success(request, "Atividade removida com sucesso!")

        except Exception as e:
            messages.error(request, f"Erro ao remover a atividade: {str(e)}")

    return render(request, 'atividades/remover_atividade.html', {
        'atividade': atividade,
        'usuario': usuario
    })