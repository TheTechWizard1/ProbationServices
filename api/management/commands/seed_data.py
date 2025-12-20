# api/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Instruction, UserProfile


class Command(BaseCommand):
    help = 'Creates initial data for ProbationServices'

    def handle(self, *args, **options):
        # Создаем примеры инструкций
        instructions = [
            {
                'title': 'Как подключить принтер',
                'content': 'Пошаговая инструкция по подключению сетевого принтера...',
                'category': 'hardware'
            },
            {
                'title': 'Сброс пароля учетной записи',
                'content': 'Инструкция по восстановлению доступа к учетной записи...',
                'category': 'account'
            },
            {
                'title': 'Настройка почтового клиента',
                'content': 'Как настроить Outlook для работы с корпоративной почтой...',
                'category': 'software'
            },
        ]

        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            for instruction_data in instructions:
                Instruction.objects.create(
                    title=instruction_data['title'],
                    content=instruction_data['content'],
                    category=instruction_data['category'],
                    created_by=admin_user
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully created initial data!')
        )