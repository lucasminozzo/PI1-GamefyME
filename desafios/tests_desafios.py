import pytest
from django.utils import timezone
from datetime import timedelta
from desafios.models import Desafio, UsuarioDesafio
from atividades.models import SessaoPomodoro
from usuarios.models import Usuario
from services import desafios_service

@pytest.mark.django_db
def test_desafio_diario_pomodoro_eh_concluido_apenas_uma_vez():
    # Setup: cria usuário e desafio
    usuario = Usuario.objects.create(nmusuario="Teste", email="teste@example.com", senha="123")
    desafio = Desafio.objects.create(
        nmdesafio="4 Pomodoros por dia",
        dsdesafio="Utilize 4 ciclos pomodoros hoje",
        tipo="diario",
        tipo_logica="pomodoro",
        parametro=4,
        expdesafio=100
    )

    # Cria 4 sessões pomodoro no dia de hoje
    agora = timezone.now()
    for _ in range(4):
        SessaoPomodoro.objects.create(
            idusuario=usuario,
            inicio=agora,
            fim=agora + timedelta(minutes=25),
            nrciclo=1
        )

    # Verifica desafios (1ª vez)
    desafios_service.verificar_desafios(usuario)
    assert UsuarioDesafio.objects.filter(idusuario=usuario, iddesafio=desafio).exists()

    # Tenta verificar novamente (não deve duplicar)
    desafios_service.verificar_desafios(usuario)
    assert UsuarioDesafio.objects.filter(idusuario=usuario, iddesafio=desafio).count() == 1

    # Simula o dia seguinte
    UsuarioDesafio.objects.all().delete()
    SessaoPomodoro.objects.all().delete()

    amanha = timezone.now() + timedelta(days=1)
    for _ in range(4):
        SessaoPomodoro.objects.create(
            idusuario=usuario,
            inicio=amanha,
            fim=amanha + timedelta(minutes=25),
            nrciclo=1
        )

    # Verifica novamente — deve premiar porque é um novo dia
    desafios_service.verificar_desafios(usuario)
    assert UsuarioDesafio.objects.filter(idusuario=usuario, iddesafio=desafio).exists()
