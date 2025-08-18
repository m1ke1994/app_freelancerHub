# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('phone', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('email', 'phone', 'role')}),
    )
    list_display = ('id', 'username', 'email', 'phone', 'role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone')
