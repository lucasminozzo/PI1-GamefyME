from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML
from atividades.models import Atividade
from services import login_service
from django.views.decorators.clickjacking import xframe_options_exempt
from datetime import datetime

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

    atividades = Atividade.objects.filter(
        idusuario=usuario,
        dtatividaderealizada__range=(data_inicio_dt, data_fim_dt)
    ).order_by('dtatividaderealizada')

    template = get_template('relatorios/atividades_relatorio.html')
    html_string = template.render({
        'usuario': usuario,
        'atividades': atividades,
        'data_inicio': data_inicio_dt,
        'data_fim': data_fim_dt,
        'now': datetime.now(),
    })

    # ESSENCIAL: base_url garante que os arquivos estáticos (fontes, imagens) funcionem!
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_atividades.pdf"'
    return response
