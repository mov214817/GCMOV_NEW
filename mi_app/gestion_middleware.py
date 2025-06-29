from django.db import connection
from django.shortcuts import redirect

class GestionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)  # 🔹 Procesa la solicitud antes de modificar la base de datos

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO gcmov;")  # ✅ Aplica solo después de procesar la solicitud
        
        return response  # 🔹 Devuelve la respuesta ya procesada

class AdminRestrictMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/") and not request.user.is_superuser:
            return redirect("login")  # 🔹 Redirige a login si no es administrador
        return self.get_response(request)