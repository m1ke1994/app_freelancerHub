# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        ("Основное", {'fields': ('username', 'password')}),
        ("Личная информация", {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'role', 'avatar')
        }),
        ("Анкета фрилансера", {
            'fields': (
                'title', 'bio', 'location', 'gender', 'education', 'status',
                'categories', 'skills',
                'rate_type', 'hourly_rate', 'project_rate', 'availability',
                'links', 'socials', 'portfolio', 'busy_dates',
            )
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
