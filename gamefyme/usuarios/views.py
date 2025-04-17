from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Usuario, TipoUsuario
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.contrib import messages

def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nmusuario')
        email = request.POST.get('emailusuario')
        senha = request.POST.get('senha')
        confsenha = request.POST.get('confsenha')
        dt_nascimento = request.POST.get('dtnascimento')

        if not all([nome, email, senha, confsenha, dt_nascimento]):
            return render(request, 'cadastro.html', {
                'erro': 'Preencha todos os campos.',
                'nmusuario': nome,
                'emailusuario': email,
                'dtnascimento': dt_nascimento
            })

        if senha != confsenha:
            return render(request, 'cadastro.html', {
                'erro': 'Senhas não coincidem.',
                'nmusuario': nome,
                'emailusuario': email,
                'dtnascimento': dt_nascimento
            })

        if Usuario.objects.filter(emailusuario=email).exists():
            return render(request, 'cadastro.html', {
                'erro': 'Já existe um usuário com esse e-mail cadastrado.',
                'erro_email': True,
                'nmusuario': nome,
                'emailusuario': email,
                'dtnascimento': dt_nascimento
            })

        try:
            usuario = Usuario(
                nmusuario=nome,
                emailusuario=email,
                senha=make_password(senha),
                dtnascimento=dt_nascimento,
                flsituacao=True,
                nivelusuario=1,
                expusuario=0,
                tipousuario=TipoUsuario.COMUM
            )
            usuario.save()
            messages.success(request, 'Usuário cadastrado com sucesso! Faça login para continuar.')
            return redirect(reverse('login'))
        except IntegrityError:
            return render(request, 'cadastro.html', {
                'erro': 'Já existe um usuário com esse e-mail cadastrado.',
                'erro_email': True,
                'nmusuario': nome,
                'emailusuario': email,
                'dtnascimento': dt_nascimento
            })

    return render(request, 'cadastro.html')

def login(request):
    return render(request, 'login.html')