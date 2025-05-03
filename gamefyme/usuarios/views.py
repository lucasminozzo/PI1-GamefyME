from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Usuario, TipoUsuario
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from services import login_service, atividades_service
from django.core.mail import send_mail
from gamefyme.settings import EMAIL_HOST_USER
from atividades.models import Atividade
from django.shortcuts import render

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth import get_user_model
from django.utils import timezone


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
                    password=make_password(senha),
                    dtnascimento=dt_nascimento,
                    flsituacao=True,
                    nivelusuario=1,
                    expusuario=0,
                    tipousuario=TipoUsuario.COMUM
                )
                usuario.save()

                try:
                    messages.success(request, 'Usuário cadastrado com sucesso! Faça login para continuar.')
                    return redirect('usuarios:login')
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
            if check_password(senha, usuario.password):
                request.session['usuario_id'] = usuario.idusuario
                request.session['usuario_nome'] = usuario.nmusuario
                atividades_service.verificar_streak_no_login(usuario)
                usuario.last_login = timezone.now()
                usuario.save()
                return redirect('usuarios:main')
            else:
                return render(request, 'login.html', {'erro': 'Email ou senha incorretos.', 'email': email})
        except Usuario.DoesNotExist:
            return render(request, 'login.html', {'erro': 'Usuário não encontrado.', 'email': email})
    return render(request, 'login.html')

def esqueceu(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            usuario = Usuario.objects.get(emailusuario=email)
            if email == usuario.emailusuario:
                id=usuario.idusuario
                uidb64 = urlsafe_base64_encode(force_bytes(id)) ## Codifica o ID do usuário
                token = default_token_generator.make_token(usuario) ## Cria um token para o usuário
                url = reverse('usuarios:nova_senha', kwargs={'uidb64': uidb64, 'token': token}) ## URL para redefinir a senha
                subject = "Esqueceu a senha - Gamefyme" ## Assunto do e-mail
                message = "Clique no link abaixo para redefinir sua senha:\n\n" ## Mensagem do e-mail
                message += f"{request.build_absolute_uri(url)}\n\n" ## Link para redefinir a senha
                message += "Se você não solicitou essa alteração, ignore este e-mail." ## Mensagem do e-mail
                send_mail(subject, message, EMAIL_HOST_USER, [email], fail_silently=True) ## Envia o e-mail
                messages.success(request, 'Email enviado com sucesso! Verifique sua caixa de entrada.') ## Mensagem de sucesso caso o e-mail tenha sido enviado
                return redirect('usuarios:login') ## Redireciona para a página de login
            else:
                return render(request, 'esqueceu.html', {'erro': 'Email incorreto.', 'email': email}) ## Mensagem de erro caso o e-mail esteja incorreto
        except Usuario.DoesNotExist:
            return render(request, 'esqueceu.html', {'erro': 'Usuário não encontrado.', 'email': email}) ## Mensagem de erro caso o usuário não exista
    return render(request, 'esqueceu.html')

def logout(request):
    request.session.flush()
    return redirect('usuarios:login')

def main(request):
    if not login_service.is_usuario_logado(request):
        return redirect('usuarios:login')

    usuario = login_service.get_usuario_logado(request)

    atividades_recorrentes = Atividade.objects.filter(
        idusuario=usuario,
        situacao=Atividade.Situacao.ATIVA,
        recorrencia=Atividade.Recorrencia.RECORRENTE
    )

    atividades_unicas = Atividade.objects.filter(
        idusuario=usuario,
        situacao=Atividade.Situacao.ATIVA,
        recorrencia=Atividade.Recorrencia.UNICA,
        dtatividaderealizada__isnull=True
    )

    return render(request, 'main.html', {
        'usuario': usuario,
        'atividades_unicas': atividades_unicas,
        'atividades_recorrentes': atividades_recorrentes
    })
    
def nova_senha(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            senha = request.POST.get('senha')
            confsenha = request.POST.get('confsenha')

            if not senha or not confsenha:
                return render(request, 'nova_senha.html', {
                    'erro': 'Preencha todos os campos.',
                    'usuario': user,
                    'uidb64': uidb64,
                    'token': token,
                })

            if senha != confsenha:
                return render(request, 'nova_senha.html', {
                    'erro': 'Senhas não coincidem.',
                    'usuario': user,
                    'uidb64': uidb64,
                    'token': token,
                })

            try:
                usuario = Usuario.objects.get(emailusuario=user.emailusuario) 
                usuario.password = make_password(senha)
                usuario.save()
                messages.success(request, 'Senha alterada com sucesso! Faça login para continuar.')
                return redirect('usuarios:login')
            except Usuario.DoesNotExist:
                return render(request, 'nova_senha.html', {
                    'erro': 'Usuário não encontrado.',
                    'usuario': user,
                    'uidb64': uidb64,
                    'token': token,
                })

        ## renderiza o formulário
        return render(request, 'nova_senha.html', {
            'usuario': user,
            'uidb64': uidb64,
            'token': token,
        })
    
    messages.error(request, 'Link inválido. Senha já foi alterada ou o link expirou.') ## Mensagem de erro caso o link seja inválido
    return redirect('usuarios:login') ## Redireciona para a página de login