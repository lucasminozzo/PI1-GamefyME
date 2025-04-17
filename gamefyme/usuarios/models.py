from django.db import models

from django.db import models

class TipoUsuario(models.TextChoices):
    ADMIN = 'admin', 'Administrador'
    COMUM = 'comum', 'Comum'

class Usuario(models.Model):
    idusuario = models.AutoField(primary_key=True)
    nmusuario = models.CharField(max_length=50)
    emailusuario = models.EmailField(max_length=254)
    senha = models.CharField(max_length=20)
    dtnascimento = models.DateField()
    flsituacao = models.BooleanField()
    nivelusuario = models.IntegerField()
    expusuario = models.SmallIntegerField()
    tipousuario = models.CharField(
        max_length=10,
        choices=TipoUsuario.choices,
        default=TipoUsuario.COMUM
    )

    class Meta:
            db_table = 'usuarios'