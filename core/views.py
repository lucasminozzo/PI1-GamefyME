from django.shortcuts import render, redirect
from services import login_service

def index(request):
    if login_service.is_usuario_logado(request):
        return redirect('usuarios:main')
    
    return render(request, 'core/index.html')

def sobre(request):
    return render(request, 'core/sobre.html')
    
def gamificacao(request):
    return render(request, 'core/gamificacao.html')