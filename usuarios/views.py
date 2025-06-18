import os
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Usuario, TipoUsuario, Notificacao
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError, transaction
from django.contrib import messages
from services import login_service, notificacao_service, desafios_service, conquistas_service
from django.core.mail import send_mail
from gamefyme.settings import EMAIL_HOST_USER
from atividades.models import Atividade
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import date
from django.conf import settings
from .forms import ConfigUsuarioForm

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from django.template.loader import render_to_string

def cadastro(request): ## RF 01 - Cadastro de usuário
    if login_service.is_usuario_logado(request):
        return redirect('usuarios:main')

    if request.method == 'POST':
        nome = request.POST.get('nmusuario')
        email = request.POST.get('emailusuario')
        senha = request.POST.get('senha')
        confsenha = request.POST.get('confsenha')
        dt_nascimento = request.POST.get('dtnascimento')

        contexto = {
            'nmusuario': nome,
            'emailusuario': email,
            'dtnascimento': dt_nascimento
        }

        if not all([nome, email, senha, confsenha, dt_nascimento]):
            contexto['erro'] = 'Preencha todos os campos.'
            return render(request, 'cadastro.html', contexto)

        if senha != confsenha:
            contexto['erro'] = 'Senhas não coincidem.'
            return render(request, 'cadastro.html', contexto)

        try:
            # Validação personalizada de senha
            validate_password(senha)

        except DjangoValidationError as e:
            contexto['erro'] = 'Senha inválida: ' + ' '.join(e.messages)
            return render(request, 'cadastro.html', contexto)

        if Usuario.objects.filter(emailusuario=email).exists():
            contexto.update({
                'erro': 'Já existe um usuário com esse e-mail cadastrado.', ## RF 01 - RN 1 - Todo usuário deve ter um cadastro único identificado por e-mail.
                'erro_email': True,
            })
            return render(request, 'cadastro.html', contexto)

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

                messages.success(request, 'Usuário cadastrado com sucesso! Faça login para continuar.')
                return redirect('usuarios:login')

        except IntegrityError:
            contexto.update({
                'erro': 'Erro de integridade ao salvar. Verifique os dados e tente novamente.',
                'erro_email': True,
            })
        except Exception:
            contexto['erro'] = 'Erro ao realizar cadastro. Tente novamente.'

        return render(request, 'cadastro.html', contexto)

    email = request.GET.get('emailusuario', '')
    return render(request, 'cadastro.html', {'emailusuario': email})

def login(request): ## RF 02 - Login de usuário
    
    if login_service.is_usuario_logado(request):
        return redirect('usuarios:main')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        try:
            usuario = Usuario.objects.get(emailusuario=email)
            if (usuario.is_active == False):
                return render(request, 'login.html', {'erro': 'Usuário inativo. Solicite uma nova senha.'})
            if check_password(senha, usuario.password):
                request.session['usuario_id'] = usuario.idusuario
                request.session['usuario_nome'] = usuario.nmusuario
                usuario.last_login = timezone.now()
                usuario.save()
                return redirect('usuarios:main')
            else:
                return render(request, 'login.html', {'erro': 'Email ou senha incorretos.', 'email': email})
        except Usuario.DoesNotExist:
            return render(request, 'login.html', {'erro': 'Usuário não encontrado.', 'email': email})
    return render(request, 'login.html')

def esqueceu(request): ## RF 02 - Esqueci minha senha 
    if login_service.is_usuario_logado(request):
        return redirect('usuarios:main')
    
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
    pasta_avatars = os.path.join(settings.BASE_DIR, 'static', 'img', 'avatares')
    arquivos = sorted(f for f in os.listdir(pasta_avatars) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')))
    desafios_service.verificar_desafios(usuario)
    conquistas_service.verificar_conquistas(usuario)

    atividades_recorrentes = Atividade.objects.filter(
        idusuario=usuario,
        situacao=Atividade.Situacao.ATIVA,
        recorrencia=Atividade.Recorrencia.RECORRENTE
    )
    atividades_unicas = Atividade.objects.filter(
        idusuario=usuario,
        situacao=Atividade.Situacao.ATIVA,
        recorrencia=Atividade.Recorrencia.UNICA
    )
    notificacoes = notificacao_service.listar_nao_lidas(usuario)
    notificacoes_nao_lidas = notificacao_service.contar_nao_lidas(usuario)
    todas_notificacoes = notificacao_service.listar_todas(usuario)
    html_todas = render_to_string('_notificacoes_lista.html', {'notificacoes': todas_notificacoes}, request=request)

    return render(request, 'main.html', {
        'usuario': usuario,
        'streak_data': usuario.streak_data,
        'streak_atual': usuario.streak_atual,
        'atividades_recorrentes': atividades_recorrentes,
        'atividades_unicas': atividades_unicas,
        'notificacoes': notificacoes,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'html_todas_notificacoes': html_todas,
        'today': date.today(),
        'avatares_disponiveis': arquivos,
    })

    
def nova_senha(request, uidb64, token): ## RF 02 - Nova senha
    if login_service.is_usuario_logado(request):
        return redirect('usuarios:main')
    
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
                if usuario.is_active == False:
                    usuario.is_active = True
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

        return render(request, 'nova_senha.html', {
            'usuario': user,
            'uidb64': uidb64,
            'token': token,
        })
    
    messages.error(request, 'Link inválido. Senha já foi alterada ou o link expirou.')
    return redirect('usuarios:login')

@require_POST
def marcar_notificacao_lida(request, notificacao_id):  ## RF 06 - Manter notificações
    if not login_service.is_usuario_logado(request):
        return JsonResponse({'success': False, 'error': 'Usuário não autenticado'}, status=401)

    usuario = login_service.get_usuario_logado(request)

    try:
        notificacao = Notificacao.objects.get(
            idnotificacao=notificacao_id,
            idusuario=usuario
        )
        notificacao_service.marcar_como_lida(notificacao)
        return JsonResponse({'success': True})
    except Notificacao.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notificação não encontrada'}, status=404)

@require_POST
def marcar_todas_lidas(request): ## RF 06 - Manter notificações
    if not login_service.is_usuario_logado(request):
        return JsonResponse({'success': False, 'error': 'Usuário não autenticado'}, status=401)

    usuario = login_service.get_usuario_logado(request)
    notificacao_service.marcar_todas_como_lidas(usuario)

    return JsonResponse({'success': True})

def ajax_todas_notificacoes(request):
    if not login_service.is_usuario_logado(request):
        return JsonResponse({'success': False}, status=403)

    usuario = login_service.get_usuario_logado(request)
    notificacoes = notificacao_service.listar_todas(usuario)

    html = render_to_string(
        '_notificacoes_lista.html',
        {'notificacoes': notificacoes},
        request=request
    )
    return JsonResponse({'success': True, 'html': html})
 
@require_POST
def atualizar_config_usuario(request): ##  RF 01 - Manter usuário
    usuario = login_service.get_usuario_logado(request)
    form = ConfigUsuarioForm(request.POST, instance=usuario)

    if form.is_valid():
        # Primeiro atualiza os dados do formulário
        form.save()

        nova_senha = request.POST.get('nova_senha')
        senha_atual = request.POST.get('senha_atual')
        
        if nova_senha:
            if not usuario.check_password(senha_atual):
                return JsonResponse({
                    'success': False,
                    'errors': {'senha_atual': ["Senha atual incorreta."]}
                }, status=400)
        
            try:
                validate_password(nova_senha, user=usuario)
                usuario.password = make_password(nova_senha)
                usuario.save()
            except DjangoValidationError as e:
                return JsonResponse({
                    'success': False,
                    'errors': {'nova_senha': e.messages}
                }, status=400)

        return JsonResponse({
            'success': True,
            'nmusuario': usuario.nmusuario,
            'dtnascimento': usuario.dtnascimento,
            'emailusuario': usuario.emailusuario,
        })

    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)
    
    
@require_POST
def atualizar_avatar(request):
    if not login_service.is_usuario_logado(request):
        return JsonResponse({'success': False, 'error': 'Usuário não autenticado'}, status=401)

    usuario = login_service.get_usuario_logado(request)
    novo_avatar = request.POST.get('imagem_perfil')

    if not novo_avatar:
        return JsonResponse({'success': False, 'error': 'Nenhum avatar selecionado'}, status=400)

    usuario.imagem_perfil = novo_avatar
    usuario.save()
    return JsonResponse({'success': True, 'imagem_perfil': novo_avatar})

def listar_usuarios(request):
    if not login_service.is_usuario_logado(request):
        return redirect('usuarios:login')

    usuario = login_service.get_usuario_logado(request)
    if usuario.tipousuario != 'administrador':
        return redirect('usuarios:main')
    
    notificacoes = notificacao_service.listar_nao_lidas(usuario)
    notificacoes_nao_lidas = notificacao_service.contar_nao_lidas(usuario)
    todas_notificacoes = notificacao_service.listar_todas(usuario)
    html_todas = render_to_string('_notificacoes_lista.html', {'notificacoes': todas_notificacoes}, request=request)
    
    usuarios = Usuario.objects.exclude(idusuario=usuario.idusuario).order_by('nmusuario')
    return render(request, 'listar_usuarios.html', {
        'usuario': usuario,
        'usuarios': usuarios,
        'notificacoes': notificacoes,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'html_todas_notificacoes': html_todas,
    })

@require_POST
def alterar_tipo_usuario(request, idusuario): ## RF 01 - Manter usuário - ADM Define tipo de usuário
    usuario_logado = login_service.get_usuario_logado(request)

    if usuario_logado.tipousuario != 'administrador' or usuario_logado.idusuario == idusuario:
        return redirect('usuarios:listar_usuarios')

    alvo = get_object_or_404(Usuario, pk=idusuario)
    alvo.tipousuario = 'comum' if alvo.tipousuario == 'administrador' else 'administrador'
    alvo.save()
    messages.success(request, f"Tipo de usuário de {alvo.nmusuario} atualizado para {alvo.get_tipousuario_display()}.")
    return redirect('usuarios:listar_usuarios')

@require_POST
def alternar_situacao_usuario(request, idusuario): ## RF 01 - Manter usuário - ADM ativa ou desativa usuário
    usuario_logado = login_service.get_usuario_logado(request)

    if usuario_logado.tipousuario != 'administrador' or usuario_logado.idusuario == idusuario:
        return redirect('usuarios:listar_usuarios')

    alvo = get_object_or_404(Usuario, pk=idusuario)
    alvo.flsituacao = not alvo.flsituacao
    alvo.is_active = alvo.flsituacao
    alvo.save()

    status = "ativado" if alvo.flsituacao else "desativado"
    messages.success(request, f"Usuário {alvo.nmusuario} foi {status}.")
    return redirect('usuarios:listar_usuarios')

def deletar_usuario(request): ## RF 01 - Manter usuário - Usuário desativando usuário
                              ## RN 02 - O próprio usuário irá requisitar ao sistema para que ele assuma o estado de “inativo”.
    if not login_service.is_usuario_logado(request):
        return redirect('usuarios:login')

    usuario = login_service.get_usuario_logado(request)
    usuario.is_active = False
    usuario.save()
    request.session.flush()
    messages.success(request, 'Usuário deletado com sucesso.')
    return redirect('usuarios:login')
