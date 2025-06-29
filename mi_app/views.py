from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import connection  
from django.http import HttpResponse
from django.contrib.auth.models import User
from mi_app.utils import obtener_cliente, registrar_cliente, guardar_o_actualizar_cliente 
from django.contrib.auth.decorators import login_required
from mi_app.models import Usuario, Estado, Ciudad, Region, Archivos
from django.contrib.sessions.models import Session
from django.utils.timezone import now
from django.http import JsonResponse
from datetime import date
import random
import os
from django.conf import settings
import pymupdf    # PyMuPDF
fitz = pymupdf  # Asignar pymupdf a fitz
import re
from django.contrib import messages
## funcion utilizada para codigo del cliente nuevo a registrar
def generar_codigo():
    return random.randint(100000, 999999)

@login_required
def register_view(request):
    if not request.user.is_superuser:  # 🔹 Solo el administrador puede registrar usuarios
        return redirect("menu")  # 🔹 Redirige al menú si no tiene permisos

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        is_admin = request.POST.get("is_admin") == "on"  # 🔹 Captura si el usuario será administrador

        if User.objects.filter(username=username).exists():
            return render(request, "mi_app/register.html", {"error": "El usuario ya existe"})

        # 🔹 Crear usuario con permisos adecuados
        user = User.objects.create_user(username=username, password=password)
        user.is_superuser = is_admin  # 🔹 Si es admin, darle permisos de superusuario
        user.is_staff = is_admin  # 🔹 Permiso para acceder al panel de Django
        user.save()

        return redirect("listar_usuarios")  # 🔹 Redirigir al listado de usuarios

    return render(request, "mi_app/register.html")

@login_required
def listar_usuarios(request):
    if not request.user.is_admin:  # 🔹 Solo el administrador puede acceder
        return redirect("menu")

    usuarios = User.objects.all()
    return render(request, "mi_app/listar_usuarios.html", {"usuarios": usuarios})

@login_required
def editar_usuario(request, user_id):
    if not request.user.is_admin:  # 🔹 Solo el administrador puede editar
        return redirect("menu")

    usuario = User.objects.get(id=user_id)

    if request.method == "POST":
        nuevo_username = request.POST.get("username")
        nueva_password = request.POST.get("password")

        usuario.username = nuevo_username
        if nueva_password:
            usuario.set_password(nueva_password)  # 🔹 Cambiar contraseña si es nueva
        usuario.save()

        return redirect("listar_usuarios")  # 🔹 Redirigir a la lista de usuarios

    return render(request, "mi_app/editar_usuario.html", {"usuario": usuario})

@login_required
def eliminar_usuario(request, user_id):
    if not request.user.is_admin:  # 🔹 Solo el administrador puede eliminar
        return redirect("menu")

    usuario = User.objects.get(id=user_id)
    usuario.delete()  # 🔹 Eliminar usuario de la BD

    return redirect("listar_usuarios")  # 🔹 Redirigir a la lista de usuarios


################ LOGIN_VIEW ################
 
@csrf_protect  # ✅ Protege la vista con CSRF

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # ✅ Crear una sesión única basada en IP y User-Agent
            user_agent = request.META.get("HTTP_USER_AGENT", "unknown")
            ip = request.META.get("REMOTE_ADDR", "unknown")
            session_key = f"{user.username}_{ip}_{user_agent}"
            
            request.session["usuario_activo"] = session_key  # ✅ Almacena sesión única
            request.session.modified = True   
            return redirect("menu")  
        else:
            return render(request, "mi_app/login.html", {"error": "Credenciales incorrectas"})

    return render(request, "mi_app/login.html")




def home_view(request):
    return render(request, 'mi_app/home.html')

################# menu_view	#####################
def menu_view(request):
    if not request.user.is_authenticated:
        return redirect("login")  
    
    # ✅ Obtener la sesión única almacenada
    session_key = request.session.get("usuario_activo", None)

    if session_key:
        username = session_key.split("_")[0]  # ✅ Extraer solo el username de la sesión
        usuario_actual = Usuario.objects.get(username=username)
        opciones = usuario_actual.opciones_menu.all()
    else:
        opciones = []

    return render(request, "mi_app/menu.html", {"opciones_menu": opciones})  


################### cliente_view ######################
def cliente_view(request):
    return render(request, 'mi_app/validacliente.html') 

#### VALIDA CLIENTE ####
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from .utils import obtener_archivos_cliente  # si lo tenés en utils.py

def validar_cliente_view(request, rif=None, paso=None):
    if request.method == "POST":
        t_rif = request.POST.get('tiporif')
        nro_rif = request.POST.get('rif')
        rif = f"{t_rif}{nro_rif}"
        rifcliente = f"{t_rif}-{nro_rif}"
    elif rif:
        t_rif = rif[0]
        nro_rif = rif[1:]
        rifcliente = f"{t_rif}-{nro_rif}"
    else:
        return HttpResponse("Método no permitido", status=405)

    # 🔒 Normalizamos paso: si viene como None o 'None', usamos 1
    if not paso or str(paso).lower() == "none":
        paso = 1
    else:
        paso = int(paso)

    print(f"📥 Valor recibido para RIF: {rifcliente} | Paso: {paso}")

    cliente = obtener_cliente(t_rif, nro_rif)
    if cliente:
        archivos = obtener_archivos_cliente(rif)

        return render(request, 'mi_app/regcliente.html', {
            'codcli': cliente['codcli_db'],
            'valrif': cliente['rif_db'],
            'razsc': cliente['razsc_db'],
            'fecha': cliente['fechreg_db'],
            'idregion': cliente['idregion_db'],
            'idstate': cliente['idstate_db'],
            'idciudad': cliente['idciudad_db'],
            'obs': cliente['obs_db'],
            'mostrar_botones': False,
            'valor': "1",
            'name_file': rif,
            'archivos': archivos,
            'paso_actual': paso
        })
    else:
        return render(request, 'mi_app/validacliente.html', {
            'valrif': rifcliente,
            'tipo_rif': t_rif,
            'rif': nro_rif,
            'valor': "0",
            'mostrar_botones': True
        })

#### REGISTRA CLIENTE ####
def registrar_cliente_view(request):
    print("*********entro******:")
    
    if request.method == "POST":
        tipo_rif = request.POST.get("hddtipcli")
        rif = request.POST.get("hdd_rif")
        documento_rif = request.FILES.get("documento_rif")

        

        if not documento_rif:
            print("❌ No se adjuntó un documento PDF")
            return render(request, "mi_app/regcliente.html", {"error": "Debe adjuntar un archivo PDF.", "valrif": f"{tipo_rif}{rif}"})

        # 📂 Guardar el archivo en MEDIA_ROOT
        file_path = os.path.join(settings.MEDIA_ROOT, documento_rif.name)
        with open(file_path, "wb+") as destination:
            for chunk in documento_rif.chunks():
                destination.write(chunk)

        print(f"✅ Archivo guardado en: {file_path}")

     
        # 🛠 Extraer RIF del PDF guardado
       ### LLAM LA FUNCION  extraer_rif_de_pdf() PARA EXTRAER LOS DATOS DEL PDF
        
        rif_extraido, nombre_extraido = extraer_rif_de_pdf(file_path)
        razon_social = nombre_extraido
        print(f"✅ Solo el RIF: {rif_extraido}")
        print(f"✅ Solo el nombre: {nombre_extraido}")


        if not rif_extraido:
            print("❌ No se pudo extraer el RIF correctamente.")
            return render(request, "mi_app/validacliente.html", {"error": "No se encontró un número de RIF válido en el documento PDF.", "valrif": f"{tipo_rif}-{rif}"})

        rifcliente = f"{tipo_rif}{rif}"
        print(f"Comparando RIF ingresado ({rifcliente}) con RIF extraído ({rif_extraido})")

        if rifcliente != rif_extraido:
            error_rif = 'error'
            print("❌ Error: El RIF del documento no coincide con el ingresado.")
            return render(request, 'mi_app/validacliente.html', {'error_rif': error_rif})
           

    #### REGISTRA CLIENTE #####
    ###########################
    codcli = generar_codigo()
    fechactual = date.today().strftime('%d/%m/%Y') 
    registrar_cliente(codcli, tipo_rif, rif,razon_social,fechactual)
    
    print(f"✅ Cliente registrado con código {codcli}")
    # Ahora sí renderizas la plantilla con todo

    return render(request, "mi_app/regcliente.html", {
                    "valrif": rifcliente,
                    "razsc": razon_social,
                    "fecha": fechactual    
    })
    #if request.method == "POST"
   # print("🔄 Redirigiendo a cliente porque no fue un POST")
    #return redirect("cliente")


def extraer_rif_de_pdf(file_path):
    print("DENTRO DE extraer_rif_de_pdf")
    doc = fitz.open(file_path)

    for page in doc:
        texto = page.get_text("text")
        for line in texto.splitlines():
            match = re.match(r'([JVGEP]\d{9})\s+([A-ZÁÉÍÓÚÑ\s]{5,50})$', line.strip())
            if match:
                rif_extraido = match.group(1).strip()
                nombre_extraido = match.group(2).strip()
                print(f"✅ RIF: {rif_extraido}, Nombre: {nombre_extraido}")
                return rif_extraido, nombre_extraido

    print("❌ No se encontró un RIF con nombre válido en el documento.")
    return None, None

   
   
#####  MUESTRA TODA LA INFO DEL RIF PDF
def verificar_pdf(file_path):
    print(f"DENTRO VERIFICAR")
    try:
        doc = fitz.open(file_path)
        texto = ""
        for page in doc:
            texto += page.get_text("text") + "\n"
        
        print("✅ Contenido del PDF:")
        print(texto)  # 📌 Esto mostrará el contenido extraído del PDF
        
    except Exception as e:
        print(f"❌ Error al abrir el PDF: {e}")
        return None

    return texto  # Devuelve el texto para análisis

##### GUARDA ARCHIVOS ######

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os

 
@login_required
def adjuntar_archivos_view(request):
    if request.method == "POST":
        namefile = request.POST.get("hdd_namefile")
        doc_ci = request.FILES.get("doc_ci")
        doc_reg_mer = request.FILES.get("doc_reg_mercantil")

        errores = []
        for nombre, archivo in [("Cédula", doc_ci), ("Registro Mercantil", doc_reg_mer)]:
            if not archivo:
                errores.append(f"Debe adjuntar archivo de {nombre}.")
            elif not archivo.name.lower().endswith(".pdf"):
                errores.append(f"El archivo de {nombre} debe ser un PDF.")

        if errores:
            for e in errores:
                messages.error(request, e)
            return redirect("validar_cliente_con_paso", rif=namefile, paso=2)

        ruta_base = f"archivos_clientes/{namefile}/"
        ruta_ci = os.path.join(ruta_base, "cedula.pdf")
        ruta_mer = os.path.join(ruta_base, "reg_mercantil.pdf")

        # 🔁 Reemplazar si ya existe
        if default_storage.exists(ruta_ci):
            default_storage.delete(ruta_ci)
        if default_storage.exists(ruta_mer):
            default_storage.delete(ruta_mer)

        # 💾 Guardar archivos nuevos
        default_storage.save(ruta_ci, ContentFile(doc_ci.read()))
        default_storage.save(ruta_mer, ContentFile(doc_reg_mer.read()))

        print(f"📁 Archivos reemplazados para: {namefile}")
        messages.success(request, "Archivos guardados correctamente.")

        return redirect("validar_cliente_con_paso", rif=namefile, paso=2)

    return HttpResponse("Método no permitido", status=405)


####### REGIONES #######
def get_regiones(request):
    region = Region.objects.filter(show_ind='Y').values('idregion', 'region_name')
    data = [{"idregion": s["idregion"], "region_name": s["region_name"]} for s in region]
    return JsonResponse(data, safe=False)

####### ESTADO #######
def get_state(request, idregion):
    estados = Estado.objects.filter(idregion=idregion, show_ind='Y').values('id_state', 'state_name')
    data = [{"id_state": e["id_state"], "state_name": e["state_name"]} for e in estados]
    return JsonResponse(data, safe=False)


####### CIUDAD #######
def get_ciudad(request, estado_id):
    ciudades = Ciudad.objects.filter(id_state_id=estado_id, show_ind='Y').values('id_ciudad', 'ciudad_name')
    data = [{"id_ciudad": c["id_ciudad"], "ciudad_name": c["ciudad_name"]} for c in ciudades]
    return JsonResponse(data, safe=False)

####### MENU #######
def submenus_para(usuario, padre):
    return padre.submenus.filter(usuarios=usuario)

####### RUTA INTERFAZ #######
def solicitudes_view(request):
    return render(request, 'mi_app/validacliente.html')

def consulta_cliente_view(request): 
    return render(request, 'mi_app/validacliente.html')

def consulta_solicitud_view(request): 
    return render(request, 'mi_app/validacliente.html')

from django.shortcuts import redirect
from datetime import date
from .utils import guardar_o_actualizar_cliente  # asegúrate de importar bien

def paso1_guardar_view(request):
    if request.method == "POST":
        codcli = request.POST.get("hdd_codcli")
        campos = {
            'region': request.POST.get("cmbregion"),
            'state': request.POST.get("cmbstate"),
            'ciudad': request.POST.get("cmbciud"),
            'obs': request.POST.get("obs"),
            # más campos si agregas más
        }
      
       # print(f"❌ region: {campos['ciudad']}")
       # print(f"❌ state: {campos['ciudad']}")
        #print(f"❌ ciudad: {campos['ciudad']}")
        guardar_o_actualizar_cliente(codcli, campos)

        # 🔁 Reenvía el template y activa paso 2 visualmente
        return render(request, "mi_app/regcliente.html", {
            "codcli": codcli,
            "paso_actual": 2
        })

  
@csrf_exempt
def guardar_parcial(request):
    if request.method == "POST":
        data = json.loads(request.body)
        codcli = data.get("codcli")
        campo = data.get("nombre")
        valor = data.get("valor")

        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE gcmov.clientes SET {campo} = %s WHERE codcli = %s", [valor, codcli])

        return JsonResponse({"status": "ok"})