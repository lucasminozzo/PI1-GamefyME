from django.shortcuts import render
from django.http import HttpResponse

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    else:
        nmusuario = request.POST.get('nmusuario')
        emailusuario = request.POST.get('emailusuario')
        senha = request.POST.get('senha')
        dtnascimento = request.POST.get('dtnascimento')

        return HttpResponse(nmusuario)

def login(request):
    return render(request, 'login.html')