from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from atividades.models import Atividade
from services import login_service
from django.views.decorators.clickjacking import xframe_options_exempt
from datetime import datetime
import io
import os
from django.conf import settings

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

    # Caminho absoluto para a fonte personalizada
    font_path = os.path.join(settings.BASE_DIR, 'static/fonts/Jersey10-Regular.ttf')

    # Incluir a fonte usando @font-face no HTML gerado
    template = get_template('relatorios/atividades_relatorio.html')
    html = template.render({
        'usuario': usuario,
        'atividades': atividades,
        'data_inicio': data_inicio_dt,
        'data_fim': data_fim_dt,
        'now': datetime.now(),
        'font_path': font_path.replace('\\', '/'),  # para compatibilidade em Windows/Linux
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_atividades.pdf"'

    pisa_status = pisa.CreatePDF(
        io.BytesIO(html.encode('utf-8')),
        dest=response,
        encoding='utf-8'
    )

    if pisa_status.err:
        return HttpResponse("Erro ao gerar o PDF", status=500)
    return response
