from django.urls import path
from mi_app import views
from mi_app.views import  login_view, register_view, menu_view, home_view, cliente_view, validar_cliente_view, registrar_cliente_view, listar_usuarios, editar_usuario, eliminar_usuario, solicitudes_view
from django.conf import settings
from django.conf.urls.static import static
 

urlpatterns = [
  path('login/', login_view, name='login'), 
  path('register/', register_view, name='register'),
  path('home/', home_view, name='home'),
  path('menu/', menu_view, name='menu'),
  
  ##OPCIONES DEL MENU##
  path('clientes/', cliente_view, name='cliente'),
  path('solicitudes/', solicitudes_view, name='solicitudes'),
  
  ##ACCIONES  DEL INTERFAZ##
  path('validar_cliente/', validar_cliente_view, name='validar_cliente'),
# Cuando se redirige luego de guardar archivos (ya con RIF y paso)

path('validar_cliente/<str:rif>/<int:paso>/', views.validar_cliente_view, name='validar_cliente_con_paso'),
path('validar_cliente/<str:rif>/', views.validar_cliente_view, name='validar_cliente_rif'),

  path('registrar_cliente/', registrar_cliente_view, name='registrar_cliente'),
  path('guardar-paso1/', views.paso1_guardar_view, name='guardar_paso1'),
  path('guardar_parcial/', views.guardar_parcial, name='guardar_parcial'),  # si usas autoguardado
  path('update-cliente/', views.paso1_guardar_view, name='completardatos_cliente'),
  path('adjuntar_archivos/', views.adjuntar_archivos_view, name='adjuntar_archivos'),
  #path('muestra_doc_cliente/', views.muestra_doc_cliente, name='ver_archivos_cliente'),

  path("listar_usuarios/", listar_usuarios, name="listar_usuarios"),
  path("editar_usuario/<int:user_id>/", editar_usuario, name="editar_usuario"),
  path("eliminar_usuario/<int:user_id>/", eliminar_usuario, name="eliminar_usuario"),
  
  path('get_regiones/', views.get_regiones, name='get_regiones'),
  path('get_state/<int:idregion>/', views.get_state, name='get_state'),
  path('get_ciudad/<int:estado_id>/', views.get_ciudad, name='get_ciudad'),
  
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)