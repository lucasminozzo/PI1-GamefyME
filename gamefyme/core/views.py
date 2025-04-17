from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')

def sobre(request):
    return render(request, 'core/sobre.html')
    
def gamificacao(request):
    return render(request, 'core/gamificacao.html')