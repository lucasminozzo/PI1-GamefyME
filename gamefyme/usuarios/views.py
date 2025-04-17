from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Usuario, TipoUsuario
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.contrib.auth.hashers import check_password

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
            with transaction.atomic():
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

                try:
                    messages.success(request, 'Usuário cadastrado com sucesso! Faça login para continuar.')
                    return redirect('auth:login')
                except Exception as e:
                    transaction.set_rollback(True)
                    return render(request, 'cadastro.html', {
                        'erro': 'Erro ao finalizar cadastro. Tente novamente.',
                        'nmusuario': nome,
                        'emailusuario': email,
                        'dtnascimento': dt_nascimento
                    })

        except IntegrityError:
            return render(request, 'cadastro.html', {
                'erro': 'Já existe um usuário com esse e-mail cadastrado.',
                'erro_email': True,
                'nmusuario': nome,
                'emailusuario': email,
                'dtnascimento': dt_nascimento
            })
        except Exception as e:
            return render(request, 'cadastro.html', {
                'erro': 'Erro ao realizar cadastro. Tente novamente.',
                'nmusuario': nome,
                'emailusuario': email,
                'dtnascimento': dt_nascimento
            })
    email = request.GET.get('emailusuario', '')
    return render(request, 'cadastro.html', {'emailusuario': email})

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        try:
            usuario = Usuario.objects.get(emailusuario=email)
            if check_password(senha, usuario.senha):
                request.session['usuario_id'] = usuario.idusuario
                return redirect('usuarios:main')
            else:
                return render(request, 'login.html', {'erro': 'Senha incorreta.', 'email': email})
        except Usuario.DoesNotExist:
            return render(request, 'login.html', {'erro': 'Usuário não encontrado.', 'email': email})
    return render(request, 'login.html')

def logout(request):
    request.session.flush()
    return redirect('auth:login')

def main(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    usuario = Usuario.objects.get(pk=usuario_id)
    return render(request, 'main.html', {'usuario': usuario})