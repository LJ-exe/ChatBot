"""Configuration de l'admin Django pour les utilisateurs."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'name', 'last_name', 'age', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'name', 'last_name')
    ordering = ('-date_joined',)

    # On redéfinit complètement les fieldsets pour éviter les doublons avec
    # le champ `last_name` du UserAdmin par défaut.
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('name', 'last_name', 'age', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'name', 'last_name', 'age', 'password1', 'password2'),
        }),
    )
