from django.shortcuts import render, redirect, get_object_or_404
from .forms import AtividadeForm
from .models import Atividade
from django.utils import timezone
from services import login_service, atividades_service
from django.contrib import messages
from django.db import IntegrityError
 
# if atividade.situacao == 'realizada':
#     streak_service.atualizar_streak(usuario)

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
    
def realizar_atividade(request, idatividade):
    if not login_service.is_usuario_logado(request):
        return redirect('usuarios:login')

    usuario = login_service.get_usuario_logado(request)
    atividade = get_object_or_404(Atividade, pk=idatividade, idusuario=usuario)

    if request.method == 'POST':
        atividade.situacao = Atividade.Situacao.REALIZADA
        atividade.dtatividaderealizada = timezone.now().date()
        atividade.save()
        atividades_service.streak_service.atualizar_streak(usuario)

        messages.success(request, f'Atividade "{atividade.nmatividade}" concluída com sucesso!')
        return redirect('usuarios:main')

    return render(request, 'atividades/realizar_atividade.html', {
        'atividade': atividade,
        'usuario': usuario
    })