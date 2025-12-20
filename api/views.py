# api/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Instruction, Ticket, UserProfile
from .serializers import InstructionSerializer, TicketSerializer, RegisterSerializer, UserSerializer
# Добавь в начало файла
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import models
from django.http import HttpResponse
import csv
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# =========================
# HTML СТРАНИЦЫ
# =========================

def home(request):
    """Главная страница (HTML)"""
    context = {}

    # Добавляем последние инструкции для главной страницы
    instructions = Instruction.objects.filter(is_published=True).order_by('-created_at')[:6]
    context['instructions'] = instructions

    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        if request.user.profile.role in ['specialist', 'admin']:
            context.update({
                'open_tickets': Ticket.objects.filter(status='open').count(),
                'in_progress_tickets': Ticket.objects.filter(status='in_progress').count(),
                'resolved_tickets': Ticket.objects.filter(status='resolved').count(),
                'total_instructions': Instruction.objects.count(),
            })

    return render(request, 'api/home.html', context)


def instruction_list(request):
    """Список инструкций (HTML) с поиском и пагинацией"""
    category = request.GET.get('category', '')
    search_query = request.GET.get('search', '')

    instructions = Instruction.objects.filter(is_published=True).order_by('-created_at')

    # Применяем фильтры
    if category:
        instructions = instructions.filter(category=category)

    if search_query:
        instructions = instructions.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Статистика
    total_views = Instruction.objects.aggregate(total_views=models.Sum('view_count'))['total_views'] or 0
    total_instructions = Instruction.objects.count()

    # Пагинация
    paginator = Paginator(instructions, 6)  # 6 инструкций на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'instructions': page_obj,
        'categories': Instruction.CATEGORY_CHOICES,
        'selected_category': category,
        'total_views': total_views,
        'total_instructions': total_instructions,
    }
    return render(request, 'api/instructions.html', context)


def instruction_detail(request, pk):
    """Детали инструкции (HTML)"""
    instruction = get_object_or_404(Instruction, pk=pk, is_published=True)
    instruction.view_count += 1
    instruction.save()

    context = {'instruction': instruction}
    return render(request, 'api/instruction_detail.html', context)


@login_required
def ticket_create(request):
    """Создание заявки (HTML)"""
    # Проверяем и создаем профиль если его нет
    if not hasattr(request.user, 'profile'):
        UserProfile.objects.create(user=request.user, role='client')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        priority = request.POST.get('priority', 'medium')

        ticket = Ticket.objects.create(
            title=title,
            description=description,
            category=category,
            priority=priority,
            created_by=request.user
        )
        messages.success(request, 'Заявка успешно создана!')
        return redirect('ticket_list')

    context = {
        'categories': Instruction.CATEGORY_CHOICES,
        'priorities': Ticket.PRIORITY_CHOICES,
    }
    return render(request, 'api/ticket_create.html', context)


def ticket_list(request):
    tickets = Ticket.objects.all()

    # Для обычных пользователей показываем только их заявки
    if not request.user.profile.role in ['specialist', 'admin']:
        tickets = tickets.filter(created_by=request.user)

    # Фильтрация по поиску
    search_query = request.GET.get('search', '')
    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Фильтрация по статусу и приоритету
    status_filter = request.GET.get('status', '')
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)

    # Статистика
    today = timezone.now().date()

    context = {
        'tickets': tickets.order_by('-created_at'),
        'total_count': Ticket.objects.count(),
        'open_tickets_count': Ticket.objects.filter(status='open').count(),
        'in_progress_tickets_count': Ticket.objects.filter(status='in_progress').count(),
        'resolved_tickets_count': Ticket.objects.filter(status='resolved').count(),
        'new_today': Ticket.objects.filter(created_at__date=today).count(),
        'avg_resolution_time': 45,  # Рассчитайте из данных
        'resolved_percent': 85,  # Рассчитайте из данных
    }

    return render(request, 'api/tickets.html', context)

# =========================
# API ENDPOINTS
# =========================

@api_view(['POST'])
def register(request):
    """Регистрация пользователя (API)"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_tickets(request):
    """Мои заявки (API)"""
    tickets = Ticket.objects.filter(created_by=request.user)
    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def instructions_by_category(request, category):
    """Инструкции по категории (API)"""
    instructions = Instruction.objects.filter(category=category, is_published=True)
    serializer = InstructionSerializer(instructions, many=True)
    return Response(serializer.data)


# =========================
# PERMISSION КЛАССЫ
# =========================

class IsSpecialistOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'profile') and \
            request.user.profile.role in ['specialist', 'admin']


class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'profile') and \
            request.user.profile.role == 'client'


# =========================
# VIEWSETS
# =========================

class InstructionViewSet(viewsets.ModelViewSet):
    queryset = Instruction.objects.filter(is_published=True)
    serializer_class = InstructionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsSpecialistOrAdmin]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        instruction = self.get_object()
        instruction.view_count += 1
        instruction.save()
        return Response({"view_count": instruction.view_count})


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'profile'):
            if user.profile.role in ['specialist', 'admin']:
                return Ticket.objects.all()
            elif user.profile.role == 'client':
                return Ticket.objects.filter(created_by=user)
        return Ticket.objects.none()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'assign', 'resolve']:
            self.permission_classes = [permissions.IsAuthenticated, IsSpecialistOrAdmin]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        ticket.assigned_to = request.user
        ticket.status = 'in_progress'
        ticket.save()
        return Response({"message": f"Ticket assigned to {request.user.username}"})

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = 'resolved'
        ticket.resolved_at = timezone.now()
        ticket.solution = request.data.get('solution', '')
        ticket.save()
        return Response({"message": "Ticket resolved successfully"})


# api/views.py - добавь эти функции

def ticket_detail(request, pk):
    """Детальная страница заявки (HTML)"""
    # Проверяем и создаем профиль если его нет
    if not hasattr(request.user, 'profile'):
        UserProfile.objects.create(user=request.user, role='client')

    ticket = get_object_or_404(Ticket, pk=pk)

    # Проверяем права доступа
    if request.user.profile.role not in ['specialist', 'admin'] and ticket.created_by != request.user:
        messages.error(request, 'У вас нет доступа к этой заявке.')
        return redirect('ticket_list')

    context = {'ticket': ticket}
    return render(request, 'api/ticket_detail.html', context)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_ticket_assign(request, pk):
    """Назначить заявку на себя (API)"""
    if not hasattr(request.user, 'profile') or request.user.profile.role not in ['specialist', 'admin']:
        return Response({"error": "Доступ запрещен"}, status=status.HTTP_403_FORBIDDEN)

    ticket = get_object_or_404(Ticket, pk=pk)
    ticket.assigned_to = request.user
    ticket.status = 'in_progress'
    ticket.save()

    return Response({"message": f"Заявка назначена на {request.user.username}"})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_ticket_resolve(request, pk):
    """Решить заявку (API)"""
    if not hasattr(request.user, 'profile') or request.user.profile.role not in ['specialist', 'admin']:
        return Response({"error": "Доступ запрещен"}, status=status.HTTP_403_FORBIDDEN)

    ticket = get_object_or_404(Ticket, pk=pk)
    ticket.status = 'resolved'
    ticket.resolved_at = timezone.now()
    ticket.solution = request.data.get('solution', '')
    ticket.save()

    return Response({"message": "Заявка решена"})



@login_required
def profile(request):
    user = request.user

    # Статистика пользователя
    my_tickets = Ticket.objects.filter(created_by=user)
    my_instructions = Instruction.objects.filter(created_by=user)

    # Для специалистов - назначенные заявки
    if user.profile.role in ['specialist', 'admin']:
        assigned_tickets = Ticket.objects.filter(assigned_to=user)
        open_tickets = my_tickets.filter(status='open')
        in_progress_tickets = my_tickets.filter(status='in_progress')
        resolved_tickets = my_tickets.filter(status='resolved')
    else:
        assigned_tickets = Ticket.objects.none()
        open_tickets = my_tickets.filter(status='open')
        in_progress_tickets = my_tickets.filter(status='in_progress')
        resolved_tickets = my_tickets.filter(status='resolved')

    context = {
        'user': user,
        'my_tickets_count': my_tickets.count(),
        'open_tickets_count': open_tickets.count(),
        'in_progress_tickets_count': in_progress_tickets.count(),
        'resolved_tickets_count': resolved_tickets.count(),
        'my_instructions_count': my_instructions.count(),
        'assigned_tickets_count': assigned_tickets.count(),
        'total_instructions': Instruction.objects.count(),
        'recent_tickets': my_tickets.order_by('-created_at')[:5],

        # Проценты для прогресс-баров
        'my_tickets_percent': 100,
        'open_tickets_percent': (open_tickets.count() / max(my_tickets.count(), 1)) * 100,
        'resolved_tickets_percent': (resolved_tickets.count() / max(my_tickets.count(), 1)) * 100,
        'my_instructions_percent': (my_instructions.count() / max(Instruction.objects.count(), 1)) * 100,

        # Дополнительная статистика
        'avg_response_time': 15,  # Рассчитайте из данных
        'satisfaction_rate': 92,  # Рассчитайте из данных
    }

    return render(request, 'api/profile.html', context)


# api/views.py - обнови функцию admin_dashboard
@login_required
def admin_dashboard(request):
    """Дашборд для администраторов"""
    if not hasattr(request.user, 'profile') or request.user.profile.role not in ['specialist', 'admin']:
        messages.error(request, 'Доступ запрещен.')
        return redirect('home')

    # Статистика пользователей
    users_count = User.objects.count()
    clients_count = UserProfile.objects.filter(role='client').count()
    specialists_count = UserProfile.objects.filter(role='specialist').count()
    admins_count = UserProfile.objects.filter(role='admin').count()

    # Статистика заявок
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.filter(status='open').count()
    in_progress_tickets = Ticket.objects.filter(status='in_progress').count()
    resolved_tickets = Ticket.objects.filter(status='resolved').count()

    # Статистика по приоритетам
    urgent_tickets = Ticket.objects.filter(priority='urgent').count()
    high_tickets = Ticket.objects.filter(priority='high').count()
    medium_tickets = Ticket.objects.filter(priority='medium').count()
    low_tickets = Ticket.objects.filter(priority='low').count()

    # Статистика инструкций
    total_instructions = Instruction.objects.count()
    total_views = Instruction.objects.aggregate(total_views=models.Sum('view_count'))['total_views'] or 0

    # Статистика по категориям
    from django.db.models import Count
    categories_stats = Ticket.objects.values('category').annotate(count=Count('id')).order_by('-count')

    # Последние активности
    recent_tickets = Ticket.objects.all().order_by('-created_at')[:5]
    popular_instructions = Instruction.objects.filter(is_published=True).order_by('-view_count')[:5]

    context = {
        'users_count': users_count,
        'clients_count': clients_count,
        'specialists_count': specialists_count,
        'admins_count': admins_count,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'urgent_tickets': urgent_tickets,
        'high_tickets': high_tickets,
        'medium_tickets': medium_tickets,
        'low_tickets': low_tickets,
        'total_instructions': total_instructions,
        'total_views': total_views,
        'categories_stats': categories_stats,
        'recent_tickets': recent_tickets,
        'popular_instructions': popular_instructions,
    }

    return render(request, 'api/admin_dashboard.html', context)

def api_docs(request):
    context = {
        'base_url': request.build_absolute_uri('/'),
    }
    return render(request, 'api/api_docs.html', context)


@login_required
def export_tickets_csv(request):
    """Экспорт заявок в CSV"""
    if not hasattr(request.user, 'profile') or request.user.profile.role not in ['specialist', 'admin']:
        messages.error(request, 'Доступ запрещен.')
        return redirect('home')

    # Создаем HTTP ответ с CSV файлом
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="tickets_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    # Заголовки CSV
    writer.writerow([
        'ID', 'Тема', 'Описание', 'Категория', 'Статус',
        'Приоритет', 'Создатель', 'Исполнитель', 'Дата создания',
        'Дата решения', 'Решение'
    ])

    # Данные
    tickets = Ticket.objects.all().order_by('-created_at')
    for ticket in tickets:
        writer.writerow([
            ticket.id,
            ticket.title,
            ticket.description,
            ticket.get_category_display(),
            ticket.get_status_display(),
            ticket.get_priority_display(),
            ticket.created_by.username,
            ticket.assigned_to.username if ticket.assigned_to else '',
            ticket.created_at.strftime('%Y-%m-%d %H:%M'),
            ticket.resolved_at.strftime('%Y-%m-%d %H:%M') if ticket.resolved_at else '',
            ticket.solution or ''
        ])

    return response

def api_docs(request):
    """API документация"""
    return render(request, 'api/api_docs.html')

def home(request):
    context = {
        'instructions': Instruction.objects.all().order_by('-created_at')[:6],
        'open_tickets': Ticket.objects.filter(status='open').count(),
        'in_progress_tickets': Ticket.objects.filter(status='in_progress').count(),
        'resolved_tickets': Ticket.objects.filter(status='resolved').count(),
        'total_instructions': Instruction.objects.count(),
        'open_tickets_percent': 0,  # Рассчитайте процент
        'resolved_percent': 0,  # Рассчитайте процент
        'views_count': 1250,  # Или возьмите из статистики
    }
    return render(request, 'api/home.html', context)


@login_required
def logout_view(request):
    """Выход из системы с перенаправлением на страницу входа"""
    logout(request)
    return redirect('login')


class CustomLoginView(LoginView):
    template_name = 'api/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')



class CustomLoginView(LoginView):
    template_name = 'api/login.html'  # Указываем правильный путь
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, 'Неверное имя пользователя или пароль')
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, f'Добро пожаловать, {form.get_user().username}!')
        return super().form_valid(form)


# Или обычная функция-представление
def login_view(request):
    from django.contrib.auth.views import LoginView
    return LoginView.as_view(template_name='api/login.html')(request)



def custom_login(request):
    """Кастомный view для входа"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = AuthenticationForm()

    return render(request, 'api/login.html', {'form': form})


@login_required
def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('login')


def home(request):
    """Главная страница"""
    return render(request, 'api/home.html')