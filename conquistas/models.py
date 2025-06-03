# conquistas/models.py
from django.db import models
from usuarios.models import Usuario

class Conquista(models.Model):
    idconquista = models.AutoField(primary_key=True)
    nmconquista = models.CharField(max_length=100)
    dsconquista = models.TextField()
    nmimagem = models.TextField(blank=True)
    expconquista = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'conquistas'

    def __str__(self):
        return self.nmconquista

class UsuarioConquista(models.Model):
    idusuarioconquista = models.AutoField(primary_key=True)
    idusuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='idusuario')
    idconquista = models.ForeignKey(Conquista, on_delete=models.CASCADE, db_column='idconquista')
    dtconcessao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuario_conquistas'
        unique_together = ('idusuario', 'idconquista')
