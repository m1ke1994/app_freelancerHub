# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Группы полей на русском
    fieldsets = (
        ("Основное", {'fields': ('username', 'password')}),
        ("Личная информация", {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'role', 'avatar')
        }),
        ("Права доступа", {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ("Важные даты", {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        ("Создание пользователя", {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'phone', 'role', 'avatar',
                'is_active', 'is_staff'
            ),
        }),
    )

    list_display = ('id', 'username', 'email', 'phone', 'role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone')
    ordering = ('id',)

    # Тоже поменяем заголовки в списке
    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj)
