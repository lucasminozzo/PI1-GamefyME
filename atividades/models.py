from django.db import models
from django.conf import settings
from usuarios.models import Usuario
from django.utils import timezone
from datetime import datetime

class Atividade(models.Model):
    idatividade = models.AutoField(primary_key=True)

    class Peso(models.TextChoices):
        MUITO_FACIL = 'muito_facil', 'Muito fácil'
        FACIL = 'facil', 'Fácil'
        MEDIO = 'medio', 'Médio'
        DIFICIL = 'dificil', 'Difícil'
        MUITO_DIFICIL = 'muito_dificil', 'Muito difícil'

    class Situacao(models.TextChoices):
        ATIVA = 'ativa', 'Ativa'
        REALIZADA = 'realizada', 'Realizada'
        CANCELADA = 'cancelada', 'Cancelada'

    class Recorrencia(models.TextChoices):
        UNICA = 'unica', 'Única'
        RECORRENTE = 'recorrente', 'Recorrente'

    idusuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='idusuario'
    )
    nmatividade = models.CharField(max_length=100)
    peso = models.CharField(max_length=20, choices=Peso.choices)
    situacao = models.CharField(max_length=20, choices=Situacao.choices, default=Situacao.ATIVA)
    recorrencia = models.CharField(max_length=20, choices=Recorrencia.choices)
    dtatividade = models.DateTimeField()
    dtatividaderealizada = models.DateTimeField(null=True, blank=True)
    tpestimado = models.IntegerField()
    dsatividade = models.TextField(blank=True)
    expatividade = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'atividades'
        
class SessaoPomodoro(models.Model):
    idsessao = models.AutoField(primary_key=True)
    idusuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='idusuario'
    )
    idatividade = models.ForeignKey(
        Atividade,
        on_delete=models.CASCADE,
        db_column='idatividade'
    )
    inicio = models.DateTimeField()
    fim = models.DateTimeField(null=True, blank=True)
    nrciclo = models.IntegerField(default=1)

    class Meta:
        db_table = 'sessoes_pomodoro'

    def __str__(self):
        return f'Sessão {self.nrciclo} - Usuário {self.idusuario_id} - Atividade {self.idatividade_id}'
    
class AtividadeConcluidas(models.Model):
    idatividade_concluida = models.AutoField(primary_key=True)
    idusuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='idusuario'
    )
    idatividade = models.ForeignKey(
        Atividade,
        on_delete=models.CASCADE,
        db_column='idatividade'
    )
    dtconclusao = models.DateTimeField()

    class Meta:
        db_table = 'atividades_concluidas'

    def __str__(self):
        return f'Usuário {self.idusuario_id} - Atividade {self.idatividade_id}'