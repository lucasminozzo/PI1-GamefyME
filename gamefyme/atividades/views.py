from django.shortcuts import render, redirect
from .forms import AtividadeForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required

@login_required
def criar_atividade(request):
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