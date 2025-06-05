from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Desafio, UsuarioDesafio
from services import login_service, desafios_service, notificacao_service, conquistas_service
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from desafios.forms import DesafioForm

## RF 04 - Manter desafios
def listar_desafios(request):
    usuario = login_service.get_usuario_logado(request)
    hoje = timezone.localdate()

    notificacoes = notificacao_service.listar_nao_lidas(usuario)
    notificacoes_nao_lidas = notificacao_service.contar_nao_lidas(usuario)
    todas_notificacoes = notificacao_service.listar_todas(usuario)
    html_todas = render_to_string('_notificacoes_lista.html', {'notificacoes': todas_notificacoes}, request=request)

    desafios = [d for d in Desafio.objects.all() if d.is_ativo()]
    concluidos_qs = UsuarioDesafio.objects.filter(idusuario=usuario, flsituacao=True)

    concluidos = []
    for d in desafios:
        ud = concluidos_qs.filter(iddesafio=d).order_by('-dtpremiacao').first()
        d.dtinicio_html = d.dtinicio.strftime('%Y-%m-%dT%H:%M') if d.dtinicio else ''
        d.dtfim_html = d.dtfim.strftime('%Y-%m-%dT%H:%M') if d.dtfim else ''
        if not ud or not ud.dtpremiacao:
            continue

        dtpremiacao = getattr(ud.dtpremiacao, 'date', lambda: ud.dtpremiacao)()

        if d.tipo == 'diario':
            if dtpremiacao == hoje:
                concluidos.append(d.iddesafio)

        elif d.tipo == 'semanal':
            if dtpremiacao.isocalendar()[:2] == hoje.isocalendar()[:2]:
                concluidos.append(d.iddesafio)

        elif d.tipo == 'mensal':
            if dtpremiacao.year == hoje.year and dtpremiacao.month == hoje.month:
                concluidos.append(d.iddesafio)

        elif d.tipo == 'unico':
            concluidos.append(d.iddesafio)

    conquistas_proximas = conquistas_service.listar_conquistas_proximas(usuario)
    _, concluidos = desafios_service.listar_desafios_ativos_nao_concluidos(usuario)

    form = DesafioForm() if usuario.tipousuario == 'administrador' else None
    desafios_service.verificar_desafios(usuario)
    return render(request,'desafios/listar.html',
        {
            'usuario': usuario,
            'notificacoes': notificacoes,
            'notificacoes_nao_lidas': notificacoes_nao_lidas,
            'html_todas_notificacoes': html_todas,
            'desafios': desafios,
            'concluidos': concluidos,
            'form': form,
            'conquistas': conquistas_proximas,
        },
    )

    

@require_POST
def cadastrar_desafio(request):
    usuario = login_service.get_usuario_logado(request)
    form = DesafioForm(request.POST)
    if form.is_valid():
        form.save()
        notificacao_service.criar_notificacao(
            usuario,
            'Desafio cadastrado com sucesso!',
            'sucesso'
        )

    return redirect('desafios:listar')


@require_POST
def editar(request):
    usuario = login_service.get_usuario_logado(request)
    if usuario.tipousuario != 'administrador':
        return redirect('usuarios:main')

    iddesafio = request.POST.get('iddesafio')
    try:
        desafio = Desafio.objects.get(pk=iddesafio)
        form = DesafioForm(request.POST, instance=desafio)
        if form.is_valid():
            form.save()
            notificacao_service.criar_notificacao(usuario, 'Desafio editado com sucesso!', 'sucesso')
    except Desafio.DoesNotExist:
        notificacao_service.criar_notificacao(usuario, 'Desafio não encontrado.', 'erro')

    return redirect('desafios:listar')