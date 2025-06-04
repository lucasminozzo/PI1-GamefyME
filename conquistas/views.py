from django.shortcuts import render, redirect
from .models import Conquista, UsuarioConquista
from services import login_service, notificacao_service, desafios_service
from .forms import ConquistaForm
from django.views.decorators.http import require_POST

def listar_conquistas(request):
    usuario = login_service.get_usuario_logado(request)
    conquistas = Conquista.objects.all()
    desbloqueadas = UsuarioConquista.objects.filter(idusuario=usuario)
    desbloqueadas_ids = [uc.idconquista.idconquista for uc in desbloqueadas]
    form = ConquistaForm() if usuario.tipousuario == 'administrador' else None
    
    # Lista desafios relacionados ao usuário
    desafios_ativos, concluidos = desafios_service.listar_desafios_ativos_nao_concluidos(usuario)

    return render(request, 'conquistas/listar.html', {
        'usuario': usuario,
        'conquistas': conquistas,
        'desbloqueadas': desbloqueadas_ids,
        'form': form,
    })

@require_POST
def cadastrar_conquista(request):
    usuario = login_service.get_usuario_logado(request)
    if usuario.tipousuario != 'administrador':
        return redirect('usuarios:main')

    form = ConquistaForm(request.POST)
    if form.is_valid():
        form.save()
        notificacao_service.criar_notificacao(
            usuario,
            'Conquista cadastrada com sucesso!',
            'sucesso'
        )
    return redirect('conquistas:listar')