from django.core.management.base import BaseCommand
from services import notificacao_service

class Command(BaseCommand):
    help = 'Envia lembretes para usuários que ainda não registraram atividades hoje'

    def handle(self, *args, **kwargs):
        notificacao_service.enviar_lembretes_diarios()
        self.stdout.write(self.style.SUCCESS("Lembretes enviados com sucesso"))
