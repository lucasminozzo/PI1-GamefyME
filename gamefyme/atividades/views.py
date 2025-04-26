from django.shortcuts import render, redirect
from .forms import AtividadeForm
from django.utils import timezone
from services import login_service, atividades_service
from django.contrib import messages
from django.db import IntegrityError

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