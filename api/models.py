# api/models.py
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('client', '👤 Клиент'),
        ('specialist', '👨‍💻 Специалист'),
        ('admin', '👑 Администратор'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client', verbose_name="Роль")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    department = models.CharField(max_length=100, blank=True, verbose_name="Отдел")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Instruction(models.Model):
    CATEGORY_CHOICES = [
        ('hardware', '🖥️ Оборудование'),
        ('software', '💻 Программное обеспечение'),
        ('network', '🌐 Сеть и интернет'),
        ('account', '👤 Учетные записи'),
        ('other', '❓ Другое'),
    ]

    title = models.CharField(max_length=200, verbose_name="Заголовок инструкции")
    content = models.TextField(verbose_name="Содержание")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Категория")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Просмотры")

    class Meta:
        verbose_name = "Инструкция"
        verbose_name_plural = "Инструкции"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', '🆕 Новая'),
        ('in_progress', '🔄 В работе'),
        ('resolved', '✅ Решена'),
        ('closed', '🔒 Закрыта'),
    ]

    PRIORITY_CHOICES = [
        ('low', '🟢 Низкий'),
        ('medium', '🟡 Средний'),
        ('high', '🟠 Высокий'),
        ('urgent', '🔴 Критичный'),
    ]

    title = models.CharField(max_length=200, verbose_name="Тема заявки")
    description = models.TextField(verbose_name="Описание проблемы")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="Статус")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="Приоритет")
    category = models.CharField(max_length=50, choices=Instruction.CATEGORY_CHOICES, verbose_name="Категория")

    # Связи
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets',
                                   verbose_name="Создатель")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='assigned_tickets', verbose_name="Исполнитель")

    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Решена")

    # Решение
    solution = models.TextField(blank=True, verbose_name="Решение")
    related_instruction = models.ForeignKey(Instruction, on_delete=models.SET_NULL, null=True, blank=True,
                                            verbose_name="Связанная инструкция")

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"