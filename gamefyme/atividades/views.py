from django.shortcuts import render, redirect, get_object_or_404
from .forms import AtividadeForm
from django.utils import timezone
from services import login_service, atividades_service
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import json
from django.db import transaction
from .models import Atividade, SessaoPomodoro, Usuario

def criar_atividade(request):
    if not login_service.is_usuario_logado(request):
        return redirect('usuarios:login')

    usuario = login_service.get_usuario_logado(request)

    if request.method == 'POST':
        form = AtividadeForm(request.POST)
        if form.is_valid():
            try:
                atividade = form.save(commit=False)
                atividade.idusuario = usuario
                atividade.dtatividade = timezone.now().date()
                atividade.situacao = 'iniciada'

                atividade.expatividade = atividades_service.calcular_experiencia(
                    atividade.peso,
                    atividade.tpestimado
                )

                atividade.save()

                messages.success(request, f'Atividade "{atividade.nmatividade}" criada com sucesso!')
                return redirect('usuarios:main')
            except IntegrityError:
                messages.error(request, f'Já existe uma atividade chamada "{form.cleaned_data["nmatividade"]}". Por favor, escolha um nome diferente.')
    else:
        form = AtividadeForm()

    return render(request, 'atividades/cadastro_atividade.html', {
        'form': form,
        'usuario': usuario
    })
    
@transaction.atomic
def realizar_atividade(request, idatividade):
    if not login_service.is_usuario_logado(request):
        return redirect('usuarios:login')

    usuario = login_service.get_usuario_logado(request)
    atividade = get_object_or_404(Atividade, pk=idatividade, idusuario=usuario)

    if request.method == 'POST':
        try:
            atividade.situacao = Atividade.Situacao.REALIZADA
            atividade.dtatividaderealizada = timezone.now().date()

            exp_por_peso = {
                Atividade.Peso.LEVE: 50,
                Atividade.Peso.MEDIO: 100,
                Atividade.Peso.PESADO: 150
            }
            exp_ganha = exp_por_peso.get(atividade.peso, 50)

            usuario.expusuario += exp_ganha

            while usuario.expusuario >= 1000:
                usuario.nivelusuario += 1
                usuario.expusuario -= 1000

            atividade.save()
            usuario.save()

            atividades_service.atualizar_streak(usuario)

            messages.success(
                request,
                f'Atividade "{atividade.nmatividade}" concluída com sucesso! Você ganhou {exp_ganha} pontos de experiência!'
            )
            return redirect('usuarios:main')

        except Exception as e:
            messages.error(request, f"Erro ao salvar a atividade: {str(e)}")
            return render(request, 'atividades/realizar_atividade.html', {
                'atividade': atividade,
                'usuario': usuario
            })

    return render(request, 'atividades/realizar_atividade.html', {
        'atividade': atividade,
        'usuario': usuario
    })

@require_http_methods(["POST"])
def registrar_sessao(request):
    try:
        data = json.loads(request.body)

        if not login_service.is_usuario_logado(request):
            return JsonResponse({'success': False, 'error': 'Usuário não logado'}, status=401)

        usuario = login_service.get_usuario_logado(request)
        atividade = get_object_or_404(Atividade, pk=data['idatividade'], idusuario=usuario)

        with transaction.atomic():
            sessao = SessaoPomodoro.objects.create(
                idusuario=usuario,
                idatividade=atividade,
                inicio=data.get('inicio'),
                fim=data.get('fim'),
                nrciclo=data.get('nrciclo', 0)
            )

            if data.get('nrciclo', 0) > 0:
                exp_por_ciclo = 10
                exp_pomodoro = data['nrciclo'] * exp_por_ciclo

                usuario.expusuario += exp_pomodoro
                while usuario.expusuario >= 1000:
                    usuario.nivelusuario += 1
                    usuario.expusuario -= 1000

                usuario.save()

                return JsonResponse({
                    'success': True,
                    'message': f'Sessão registrada com sucesso! Bônus de {exp_pomodoro} pontos de experiência por usar o Pomodoro!'
                })

            return JsonResponse({'success': True, 'message': 'Sessão registrada com sucesso!'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    if not login_service.is_usuario_logado(request):
        return JsonResponse({'success': False, 'error': 'Usuário não autenticado'}, status=401)

    try:
        data = json.loads(request.body)
        usuario = login_service.get_usuario_logado(request)
        atividade = get_object_or_404(Atividade, pk=data['idatividade'], idusuario=usuario)

        SessaoPomodoro.objects.create(
            idusuario=usuario,
            idatividade=atividade,
            inicio=data['inicio'],
            fim=data['fim'],
            nrciclo=data.get('nrciclo', 0)
        )

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    