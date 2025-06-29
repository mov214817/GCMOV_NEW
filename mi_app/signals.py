from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Usuario, OpcionMenu

@receiver(m2m_changed, sender=Usuario.opciones_menu.through)
def sync_menu_assignments(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set:
            opcion = OpcionMenu.objects.get(pk=pk)
            opcion.usuarios.add(instance)
