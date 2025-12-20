# api/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Ticket, Instruction, UserProfile
import json


class TicketAPITestCase(APITestCase):
    def setUp(self):
        # Создаем пользователей
        self.client_user = User.objects.create_user(username='client', password='password123')
        self.specialist_user = User.objects.create_user(username='specialist', password='password123')

        # Создаем профили
        self.client_profile = UserProfile.objects.create(user=self.client_user, role='client')
        self.specialist_profile = UserProfile.objects.create(user=self.specialist_user, role='specialist')

        # Аутентификация
        self.client.force_authenticate(user=self.client_user)

        # Данные для теста
        self.ticket_data = {'title': 'Тестовая заявка', 'description': 'Описание тестовой заявки',
                            'category': 'hardware'}
        self.instruction_data = {'title': 'Тестовая инструкция', 'content': 'Содержание тестовой инструкции',
                                 'category': 'software'}

    def test_create_ticket(self):
        """Проверка создания заявки"""
        response = self.client.post(reverse('ticket-list'), self.ticket_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 1)
        self.assertEqual(Ticket.objects.get().title, 'Тестовая заявка')

    def test_get_tickets_for_client(self):
        """Проверка получения списка заявок для клиента"""
        # Создаем заявку от имени клиента
        Ticket.objects.create(created_by=self.client_user, **self.ticket_data)

        response = self.client.get(reverse('ticket-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_tickets_for_specialist(self):
        """Проверка получения всех заявок для специалиста"""
        # Создаем заявку от имени клиента
        Ticket.objects.create(created_by=self.client_user, **self.ticket_data)

        # Аутентификация под специалистом
        self.client.force_authenticate(user=self.specialist_user)
        response = self.client.get(reverse('ticket-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_specialist_can_assign_ticket(self):
        """Проверка назначения заявки специалистом"""
        ticket = Ticket.objects.create(created_by=self.client_user, **self.ticket_data)

        self.client.force_authenticate(user=self.specialist_user)
        response = self.client.post(reverse('ticket-assign', kwargs={'pk': ticket.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ticket.refresh_from_db()
        self.assertEqual(ticket.assigned_to, self.specialist_user)
        self.assertEqual(ticket.status, 'in_progress')


class InstructionAPITestCase(APITestCase):
    def setUp(self):
        # Создаем пользователей
        self.specialist_user = User.objects.create_user(username='specialist', password='password123')
        self.admin_user = User.objects.create_user(username='admin', password='password123', is_staff=True)

        # Создаем профили
        self.specialist_profile = UserProfile.objects.create(user=self.specialist_user, role='specialist')
        self.admin_profile = UserProfile.objects.create(user=self.admin_user, role='admin')

        # Аутентификация под специалистом
        self.client.force_authenticate(user=self.specialist_user)

        self.instruction_data = {'title': 'Тестовая инструкция', 'content': 'Содержание инструкции',
                                 'category': 'software'}

    def test_create_instruction(self):
        """Проверка создания инструкции специалистом"""
        response = self.client.post(reverse('instruction-list'), self.instruction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Instruction.objects.count(), 1)
        self.assertEqual(Instruction.objects.get().title, 'Тестовая инструкция')

    def test_get_instructions(self):
        """Проверка получения списка инструкций"""
        Instruction.objects.create(created_by=self.specialist_user, **self.instruction_data)

        # Разлогиниваемся, чтобы проверить доступ для анонимных пользователей
        self.client.logout()

        response = self.client.get(reverse('instruction-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_client_cannot_create_instruction(self):
        """Проверка, что клиент не может создать инструкцию"""
        client_user = User.objects.create_user(username='client', password='password123')
        UserProfile.objects.create(user=client_user, role='client')
        self.client.force_authenticate(user=client_user)

        response = self.client.post(reverse('instruction-list'), self.instruction_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)