from usuarios.models import Notificacao

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
