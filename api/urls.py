# api/urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tickets', views.TicketViewSet, basename='ticket')
router.register(r'instructions', views.InstructionViewSet, basename='instruction')

urlpatterns = [
    # HTML страницы
    path('', views.home, name='home'),
    path('instructions/', views.instruction_list, name='instruction_list'),
    path('instructions/<int:pk>/', views.instruction_detail, name='instruction_detail'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('api/docs/', views.api_docs, name='api_docs'),

    # Аутентификация - ВЫБЕРИТЕ ОДИН ИЗ ВАРИАНТОВ:

    # Вариант 1: Использовать кастомный view из views.py
    # path('login/', views.LoginView.as_view(), name='login'),
    # path('logout/', views.logout_view, name='logout'),

    # Вариант 2: Использовать встроенные view с указанием шаблона
    path('login/', auth_views.LoginView.as_view(template_name='api/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # API endpoints
    path('api/', include(router.urls)),
    path('api/register/', views.register, name='api_register'),
    path('api/my-tickets/', views.my_tickets, name='api_my_tickets'),
    path('api/instructions/category/<str:category>/', views.instructions_by_category,
         name='api_instructions_by_category'),

    # API действия
    path('api/tickets/<int:pk>/assign/', views.api_ticket_assign, name='api_ticket_assign'),
    path('api/tickets/<int:pk>/resolve/', views.api_ticket_resolve, name='api_ticket_resolve'),

    # Экспорт и документация
    path('api/export/tickets/csv/', views.export_tickets_csv, name='export_tickets_csv'),
    # Удалите дублирующийся path('api/docs/', ...) если он есть выше
]