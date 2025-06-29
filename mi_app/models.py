from django.db import models  
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.conf import settings


class OpcionMenu(models.Model):
    nombre = models.CharField(max_length=100)
    url = models.CharField(max_length=100, blank=True, null=True)
    padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='submenus')
    usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='menus_autorizados'
    )

    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("El usuario debe tener un nombre de usuario")
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class Usuario(AbstractUser):
    tipo_usuario = models.CharField(
        max_length=20,
        choices=[
            ("normal", "Normal"),
            ("especial", "Especial"),
            ("admin", "Administrador")
        ],
        default="normal"
    )

    opciones_menu = models.ManyToManyField(
        OpcionMenu, blank=True, related_name='usuarios_asignados'
    )

    groups = models.ManyToManyField(Group, related_name="usuario_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="usuario_permissions", blank=True)

    is_superuser = models.BooleanField(default=False)  
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()


class Reg_Cliente(models.Model):
    rif = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()

    def __str__(self):
        return f"{self.rif} - {self.nombre}"


class Region(models.Model):
    idregion = models.IntegerField(primary_key=True)
    region_code = models.CharField(max_length=10)
    region_name = models.CharField(max_length=25)
    show_ind = models.CharField(max_length=5)

    class Meta:
        db_table = 'region'
        managed = False

    def __str__(self):
        return self.region_name


class Estado(models.Model):
    id_state = models.IntegerField(primary_key=True)
    state_code = models.CharField(max_length=10)
    state_name = models.CharField(max_length=25)
    state_abr = models.CharField(max_length=5)
    show_ind = models.CharField(max_length=5)
    idregion = models.IntegerField()

    class Meta:
        db_table = 'state'
        managed = False

    def __str__(self):
        return self.state_name


class Ciudad(models.Model):
    id_ciudad = models.IntegerField(primary_key=True)
    id_state = models.ForeignKey(Estado, db_column='id_state', on_delete=models.DO_NOTHING)
    ciudad_code = models.CharField(max_length=10)
    ciudad_name = models.CharField(max_length=25)
    show_ind = models.CharField(max_length=1)

    class Meta:
        db_table = 'ciudad'
        managed = False

    def __str__(self):
        return self.ciudad_name

from django.db import models

class Archivos(models.Model):
    cliente = models.CharField(max_length=100)  # o un ForeignKey, si lo usás
    tipo = models.CharField(max_length=50)
    archivo = models.FileField(upload_to="archivos_clientes/")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cliente} - {self.tipo}"
