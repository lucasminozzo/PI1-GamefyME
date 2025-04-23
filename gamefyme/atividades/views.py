from django.shortcuts import render, redirect
from .forms import AtividadeForm
from django.utils import timezone
from services import login_service

def criar_atividade(request):
    if(not login_service.is_usuario_logado(request)):
        return redirect('auth:login')
    
    if request.method == 'POST':
        form = AtividadeForm(request.POST)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.usuario = request.user
            atividade.dtatividade = timezone.now().date()
            atividade.situacao = 'iniciada'
            atividade.save()
            return redirect('atividades:lista')
    else:
        form = AtividadeForm()
    return render(request, 'atividades/cadastro_atividade.html', {'form': form})