# api/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Instruction, Ticket

# Заголовки админки
admin.site.site_header = "ProbationServices - Панель управления"
admin.site.site_title = "ProbationServices Admin"
admin.site.index_title = "Центр управления системой"

# ==================== USER PROFILE ====================
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'date_joined']
    list_filter = ['profile__role', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_role(self, obj):
        return obj.profile.get_role_display()
    get_role.short_description = 'Роль'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# ==================== INSTRUCTION ====================
class InstructionAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_by', 'is_published', 'view_count', 'created_at']
    list_filter = ['category', 'is_published', 'created_at']
    search_fields = ['title', 'content']
    list_editable = ['is_published']
    readonly_fields = ['created_at', 'updated_at', 'view_count']

    fieldsets = (
        ('Содержание', {
            'fields': ('title', 'content', 'category')
        }),
        ('Публикация', {
            'fields': ('is_published', 'created_by', 'view_count')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Если объект создается впервые
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Instruction, InstructionAdmin)

# ==================== TICKET ====================
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'status', 'priority', 'created_by', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['title', 'description', 'solution']
    list_editable = ['status', 'priority', 'assigned_to']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']

    fieldsets = (
        ('Проблема', {
            'fields': ('title', 'description', 'category', 'priority', 'created_by')
        }),
        ('Решение', {
            'fields': ('status', 'assigned_to', 'solution', 'related_instruction', 'resolved_at')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Если объект создается впервые
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Ticket, TicketAdmin)





# ==================== USER PROFILE отдельно ====================
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'department']
    list_filter = ['role', 'department']
    search_fields = ['user__username', 'phone', 'department']
    list_editable = ['role', 'phone', 'department']

admin.site.register(UserProfile, UserProfileAdmin)