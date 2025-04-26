from django.db import models

class TipoUsuario(models.TextChoices):
    ADMIN = 'admin', 'Administrador'
    COMUM = 'comum', 'Comum'

class Usuario(models.Model):
    idusuario = models.AutoField(primary_key=True)
    nmusuario = models.CharField(max_length=50)
    emailusuario = models.EmailField(max_length=254, unique=True)
    senha = models.CharField(max_length=128)
    dtnascimento = models.DateField()
    flsituacao = models.BooleanField(default=True)
    nivelusuario = models.IntegerField(default=1)
    expusuario = models.SmallIntegerField(default=0)
    tipousuario = models.CharField(
        max_length=10,
        choices=TipoUsuario.choices,
        default=TipoUsuario.COMUM
    )

    class Meta:
        db_table = 'usuarios'