from django.utils import timezone
from django.core.mail import send_mail
from usuarios.models import Usuario, Notificacao, TipoUsuario
from gamefyme.settings import EMAIL_HOST_USER

def criar_notificacao(usuario, mensagem, tipo='info'):
    return Notificacao.objects.create(
        idusuario=usuario,
        dsmensagem=mensagem,
        fltipo=tipo
    )

def listar_nao_lidas(usuario, limite=5):
    return Notificacao.objects.filter(
        idusuario=usuario,
        flstatus=False
    ).order_by('-dtcriacao')[:limite]

def contar_nao_lidas(usuario):
    return Notificacao.objects.filter(
        idusuario=usuario,
        flstatus=False
    ).count()

def listar_todas(usuario):
    return Notificacao.objects.filter(idusuario=usuario).order_by('-dtcriacao')

def marcar_como_lida(notificacao):
    notificacao.flstatus = True
    notificacao.save()

def marcar_todas_como_lidas(usuario):
    Notificacao.objects.filter(idusuario=usuario, flstatus=False).update(flstatus=True)

def enviar_lembretes_diarios():
    hoje = timezone.now().date()
    usuarios = Usuario.objects.filter(flsituacao=True)

    for user in usuarios:
        fez_atividade = user.atividade_set.filter(dtatividaderealizada=hoje).exists()

        if not fez_atividade:
            Notificacao.objects.create(
                idusuario=user,
                dsmensagem="Não se esqueça de registrar seus hábitos hoje!",
                fltipo=Notificacao.Tipo.AVISO
            )
            send_mail(
                "GamefyME: lembrete diário",
                f"Olá {user.nmusuario}, não se esqueça de registrar seus hábitos hoje!",
                EMAIL_HOST_USER,
                [user.emailusuario],
                fail_silently=True
            )