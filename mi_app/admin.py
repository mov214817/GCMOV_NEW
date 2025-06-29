from django.contrib import admin
from django.conf import settings
from django.db import models

from django.contrib.auth.admin import UserAdmin
from .models import Usuario, OpcionMenu



@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "tipo_usuario")  
    filter_horizontal = ("opciones_menu",)  # ✅ Activa la selección de menús en el admin

    fieldsets = UserAdmin.fieldsets + (
        ("Opciones de Menú", {"fields": ("opciones_menu",)}),  # ✅ Muestra el campo en el admin
    )

@admin.register(OpcionMenu)
class OpcionMenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'url', 'padre')
    list_filter = ('padre',)
    search_fields = ('nombre',)
    filter_horizontal = ('usuarios',)