from django.shortcuts import render, redirect
from .models import Conquista, UsuarioConquista
from services import login_service, notificacao_service, conquistas_service
from .forms import ConquistaForm
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string

def listar_conquistas(request):
    usuario = login_service.get_usuario_logado(request)

    # --- INÍCIO DA CORREÇÃO: Lógica de Notificações ---
    notificacoes = notificacao_service.listar_nao_lidas(usuario)
    notificacoes_nao_lidas = notificacao_service.contar_nao_lidas(usuario)
    todas_notificacoes = notificacao_service.listar_todas(usuario)
    html_todas = render_to_string('_notificacoes_lista.html', {'notificacoes': todas_notificacoes}, request=request)

    conquistas_service.verificar_conquistas(usuario)

    conquistas = Conquista.objects.all().order_by('nmconquista')
    concluidas_ids = UsuarioConquista.objects.filter(
        idusuario=usuario
    ).values_list('idconquista_id', flat=True)

    context = {
        'usuario': usuario,
        'conquistas': conquistas,
        'concluidas_ids': concluidas_ids,
        'notificacoes': notificacoes,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'html_todas_notificacoes': html_todas,
    }
    
    return render(request, 'conquistas/listar.html', context)

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