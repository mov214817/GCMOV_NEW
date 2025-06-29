from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.filter
def get_menu(menus, nombre):
    return menus.filter(nombre=nombre).first()

@register.filter
def submenus_para(usuario, padre):
    return padre.submenus.filter(id__in=usuario.opciones_menu.values_list('id', flat=True))

@register.filter
def ruta_django(nombre_url):
    if not nombre_url:
        return None
    try:
        return reverse(nombre_url.strip().lower())
    except NoReverseMatch:
        return None

