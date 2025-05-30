from django.db import models
from usuarios.models import Usuario
from django.utils import timezone

class TipoDesafio(models.TextChoices):
    DIARIO = 'diario', 'Diário'
    SEMANAL = 'semanal', 'Semanal'
    MENSAL = 'mensal', 'Mensal'
    UNICO = 'unico', 'Único'

class Desafio(models.Model):
    iddesafio = models.AutoField(primary_key=True)
    nmdesafio = models.CharField(max_length=100)
    dsdesafio = models.TextField()
    tipo = models.CharField(max_length=10, choices=TipoDesafio.choices)
    dtinicio = models.DateTimeField(null=True, blank=True)
    dtfim = models.DateTimeField(null=True, blank=True)
    expdesafio = models.SmallIntegerField(default=0)
    tipo_logica = models.CharField(max_length=50)
    parametro = models.IntegerField(null=True, blank=True)

    def is_ativo(self):
        if self.tipo == TipoDesafio.UNICO:
            agora = timezone.now()
            return self.dtinicio and self.dtfim and self.dtinicio <= agora <= self.dtfim
        return True

    class Meta:
        db_table = 'desafios'

    def __str__(self):
        return self.nmdesafio

class UsuarioDesafio(models.Model):
    idusuariodesafio = models.AutoField(primary_key=True)
    idusuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='idusuario')
    iddesafio = models.ForeignKey(Desafio, on_delete=models.CASCADE, db_column='iddesafio')
    flsituacao = models.BooleanField(default=True)
    dtpremiacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'usuario_desafios'
        unique_together = ('idusuario', 'iddesafio')

