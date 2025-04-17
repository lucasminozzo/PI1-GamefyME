from django.shortcuts import render, redirect
from .models import Usuario, TipoUsuario

def cadastro(request):
    if request.method == 'POST':
        nome = request.POST['nmusuario']
        email = request.POST['emailusuario']
        senha = request.POST['senha']
        confsenha = request.POST['confsenha']
        dt_nascimento = request.POST['dtnascimento']

        if senha == confsenha:
            usuario = Usuario(
                nmusuario=nome,
                emailusuario=email,
                senha=senha,
                dtnascimento=dt_nascimento,
                flsituacao=True,
                nivelusuario=1,
                expusuario=0,
                tipousuario=TipoUsuario.COMUM
            )
            usuario.save()
            return redirect('/auth/login')
        else:
            return render(request, 'cadastro.html', {'error': 'Senhas não coincidem'})

    return render(request, 'cadastro.html')

def login(request):
    return render(request, 'login.html')
