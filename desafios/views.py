from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Desafio, UsuarioDesafio
from services import login_service, desafios_service, notificacao_service, conquistas_service, desafios_service
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from desafios.forms import DesafioForm
from django.db.models import Case, When, Value, IntegerField

## RF 04 - Manter desafios
def listar_desafios(request):
    usuario = login_service.get_usuario_logado(request)
    hoje = timezone.localdate()
    agora = timezone.now()

    notificacoes = notificacao_service.listar_nao_lidas(usuario)
    notificacoes_nao_lidas = notificacao_service.contar_nao_lidas(usuario)
    todas_notificacoes = notificacao_service.listar_todas(usuario)
    html_todas = render_to_string('_notificacoes_lista.html', {'notificacoes': todas_notificacoes}, request=request)

    desafios_ativos = Desafio.objects.filter(dtinicio__lte=agora, dtfim__gte=agora)
    ordem_customizada = Case(
        When(tipo='diario', then=Value(1)),
        When(tipo='semanal', then=Value(2)),
        When(tipo='mensal', then=Value(3)),
        default=Value(4),
        output_field=IntegerField(),
    )
    desafios_ordenados = desafios_ativos.annotate(
        ordem_tipo=ordem_customizada
    ).order_by('ordem_tipo', 'nmdesafio')

    concluidos_qs = UsuarioDesafio.objects.filter(idusuario=usuario, flsituacao=True)
    concluidos = []
    for d in desafios_ordenados:
        ud = concluidos_qs.filter(iddesafio=d).order_by('-dtpremiacao').first()
        d.dtinicio_html = d.dtinicio.strftime('%Y-%m-%dT%H:%M') if d.dtinicio else ''
        d.dtfim_html = d.dtfim.strftime('%Y-%m-%dT%H:%M') if d.dtfim else ''
        if not ud or not ud.dtpremiacao:
            continue
        dtpremiacao = getattr(ud.dtpremiacao, 'date', lambda: ud.dtpremiacao)()
        if d.tipo == 'diario' and dtpremiacao == hoje: concluidos.append(d.iddesafio)
        elif d.tipo == 'semanal' and dtpremiacao.isocalendar()[:2] == hoje.isocalendar()[:2]: concluidos.append(d.iddesafio)
        elif d.tipo == 'mensal' and dtpremiacao.year == hoje.year and dtpremiacao.month == hoje.month: concluidos.append(d.iddesafio)
        elif d.tipo == 'unico': concluidos.append(d.iddesafio)

    form = DesafioForm() if usuario.tipousuario == 'administrador' else None
    desafios_service.verificar_desafios(usuario)
    conquistas_service.verificar_conquistas(usuario)
    
    context = {
        'usuario': usuario,
        'desafios': desafios_ordenados,
        'concluidos': concluidos,
        'form': form,
        'notificacoes': notificacoes,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'html_todas_notificacoes': html_todas,
    }
    
    return render(request, 'desafios/listar.html', context)

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