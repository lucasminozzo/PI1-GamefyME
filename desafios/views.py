from django.shortcuts import render
from django.utils import timezone
from .models import Desafio, UsuarioDesafio
from services import login_service, atividades_service, notificacao_service
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from desafios.forms import DesafioForm

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
        ud = concluidos_qs.filter(iddesafio=d).first()
        if not ud or not ud.dtpremiacao:
            continue

        dtpremiacao = ud.dtpremiacao.date() if hasattr(ud.dtpremiacao, 'date') else ud.dtpremiacao
        if d.tipo == 'diario' and dtpremiacao == hoje:
            concluidos.append(d.iddesafio)
        elif d.tipo == 'semanal' and dtpremiacao.isocalendar()[1] == hoje.isocalendar()[1] and dtpremiacao.year == hoje.year:
            concluidos.append(d.iddesafio)
        elif d.tipo == 'mensal' and dtpremiacao.month == hoje.month and dtpremiacao.year == hoje.year:
            concluidos.append(d.iddesafio)
        elif d.tipo == 'unico':
            concluidos.append(d.iddesafio)

    form = DesafioForm() if usuario.tipousuario == 'administrador' else None

    return render(request, 'desafios/listar.html', {
        'usuario': usuario,
        'notificacoes': notificacoes,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'html_todas_notificacoes': html_todas,
        'desafios': desafios,
        'concluidos': concluidos,
        'form': form,
    })

@require_POST
def cadastrar_desafio(request):
    usuario = login_service.get_usuario_logado(request)
    if usuario.tipousuario != 'administrador':
        return redirect('usuarios:main')

    form = DesafioForm(request.POST)
    if form.is_valid():
        form.save()
        notificacao_service.criar_notificacao(usuario, 'Desafio cadastrado com sucesso!', 'sucesso')

    return redirect('desafios:listar')