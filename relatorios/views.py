from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML
from atividades.models import AtividadeConcluidas
from services import login_service
from django.views.decorators.clickjacking import xframe_options_exempt
from datetime import datetime, time

@xframe_options_exempt
def gerar_relatorio_atividades(request):
    if not login_service.is_usuario_logado(request):
        return HttpResponse("Usuário não autenticado.", status=401)

    usuario = login_service.get_usuario_logado(request)
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if not data_inicio or not data_fim:
        return HttpResponse("Parâmetros de data inválidos.", status=400)

    try:
        data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Formato de data inválido.", status=400)

    data_inicio_dt = datetime.combine(data_inicio_dt, time.min)
    data_fim_dt = datetime.combine(data_fim_dt, time.max)

    atividades_concluidas = AtividadeConcluidas.objects.filter(
        idusuario=usuario,
        dtconclusao__range=(data_inicio_dt, data_fim_dt)
    ).select_related('idatividade').order_by('dtconclusao')

    template = get_template('relatorios/atividades_relatorio.html')
    html_string = template.render({
        'usuario': usuario,
        'atividades_concluidas': atividades_concluidas,
        'data_inicio': data_inicio_dt.date(),
        'data_fim': data_fim_dt.date(),
        'now': datetime.now(),
    })

    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_atividades.pdf"'
    return response
