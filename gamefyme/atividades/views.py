from django.shortcuts import render, redirect
from .forms import AtividadeForm
from django.utils import timezone
from services import login_service
from django.contrib import messages  # Adicione esta importação

def criar_atividade(request):
    if not login_service.is_usuario_logado(request):
        return redirect('auth:login')

    usuario = login_service.get_usuario_logado(request)

    if request.method == 'POST':
        form = AtividadeForm(request.POST)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.idusuario = usuario
            atividade.dtatividade = timezone.now().date()
            atividade.situacao = 'iniciada'
            atividade.save()

            messages.success(request, 'Atividade criada com sucesso!')

            return redirect('usuarios:main')
    else:
        form = AtividadeForm()

    return render(request, 'atividades/cadastro_atividade.html', {
        'form': form,
        'usuario': usuario
    })