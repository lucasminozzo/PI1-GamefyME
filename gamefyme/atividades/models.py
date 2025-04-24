from django.db import models
from django.conf import settings

class Atividade(models.Model):
    idatividade = models.AutoField(primary_key=True)

    class Peso(models.TextChoices):
        MUITO_FACIL = 'muito_facil', 'Muito fácil'
        FACIL = 'facil', 'Fácil'
        MEDIO = 'medio', 'Médio'
        DIFICIL = 'dificil', 'Difícil'
        MUITO_DIFICIL = 'muito_dificil', 'Muito difícil'

    class Situacao(models.TextChoices):
        INICIADA = 'iniciada', 'Iniciada'
        PAUSADA = 'pausada', 'Pausada'
        REALIZADA = 'realizada', 'Realizada'
        CANCELADA = 'cancelada', 'Cancelada'

    class Recorrencia(models.TextChoices):
        UNICA = 'unica', 'Única'
        HABITUAL = 'habitual', 'Habitual'

    idusuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='idusuario'
    )
    nmatividade = models.CharField(max_length=100)
    peso = models.CharField(max_length=20, choices=Peso.choices)
    situacao = models.CharField(max_length=20, choices=Situacao.choices, default=Situacao.INICIADA)
    recorrencia = models.CharField(max_length=20, choices=Recorrencia.choices)
    dtatividade = models.DateField()
    dtatividaderealizada = models.DateField(null=True, blank=True)
    tpestimado = models.IntegerField()
    dsatividade = models.TextField(blank=True)
    expatividade = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'atividades'