from django.db import connection
import os
from django.conf import settings
from time import time
## CONSULTA CLIENTE SI EXISTE CARGA DATOS 
def obtener_cliente(tipo_rif,rif):
  
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT codcli, 
                tipcli||'-'||nrorif as rif, 
                razon_social,
                TO_CHAR(fechreg, 'DD/MM/YYYY') AS fecha, 
                idregion,
                idstate,
                idciudad,
                direccion,
                obs
            FROM gcmov.clientes
            WHERE tipcli = %s AND nrorif = %s """, [tipo_rif, rif])
        row = cursor.fetchone()

    if row:
        return {
            ### nombre de campos y posicion para cargar en el front 
            'codcli_db': row[0],
            'rif_db': row[1],
            'razsc_db': row[2],
            'fechreg_db': row[3],
            'idregion_db': row[4],
            'idstate_db': row[5],
            'idciudad_db': row[6],
             'direccion_db': row[7],
            'obs_db': row[7] 
             
        }
         
    return None
  
  #  with connection.cursor() as cursor:
   #     cursor.execute( "SELECT * FROM gcmov.clientes WHERE tipcli = %s AND nrorif = %s",[tipo_rif, rif])  # 🔹 Ajusta el esquema si es necesario
    #    cliente = cursor.fetchone()
    #return cliente  # Devuelve los datos del cliente o None si no existe

    nrorif = "{tipo_rif}{rif}"
    rif_fij="V0123456789"
    #if nrorif != rif_fij:
     #   with connection.cursor() as cursor:
       #cursor.execute( "SELECT * FROM gcmov.clientes WHERE tipcli = %s AND nrorif = %s",[tipo_rif, rif])  # 🔹 Ajusta el esquema si es necesario
      #      cliente = rif_fij
       # return cliente  # Devuelve los datos del cliente o None si no existe
   
 
## INSERTA CLIENTES
def registrar_cliente(codcli, t_rif, nro_rif, razon_social,fecha):
    print(f"Valor recibido para registrar_cliente tipocli: {t_rif}") 
    print(f"Valor recibido para registrar_cliente nrorif: {nro_rif}") 
      
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO gcmov.clientes (codcli, tipcli, nrorif,razon_social,fechreg) VALUES (%s, %s, %s, %s, %s)", [codcli,t_rif,nro_rif,razon_social,fecha])



def guardar_o_actualizar_cliente(codcli, campos):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM gcmov.clientes WHERE codcli = %s", [codcli])
        existe = cursor.fetchone()[0] > 0

        if existe:
            print("Ciudad recibida en POST:", campos["ciudad"])

            cursor.execute("""
                UPDATE gcmov.clientes   
                SET idregion = %s,
                idstate = %s,
                idciudad = %s,
                    obs = %s
                WHERE codcli = %s
            """, [
                campos['region'],
                 campos['state'],
                  campos['ciudad'],
                campos['obs'],
                codcli
            ])
            
def obtener_archivos_cliente(name_file):
    """
    Retorna los archivos existentes del cliente con su URL, agregando
    un parámetro para evitar caché del navegador.
    """
    ruta_cliente = os.path.join(settings.MEDIA_ROOT, "archivos_clientes", name_file)
    archivos = {
        "cedula": None,
        "reg_mercantil": None,
    }

    if os.path.exists(ruta_cliente):
        for archivo in os.listdir(ruta_cliente):
            nombre = archivo.lower()
            version = f"?v={int(time())}"
            url_base = f"{settings.MEDIA_URL}archivos_clientes/{name_file}/{archivo}{version}"

            if "cedula" in nombre:
                archivos["cedula"] = {
                    "nombre": archivo,
                    "url": url_base
                }
            elif "reg_mercantil" in nombre:
                archivos["reg_mercantil"] = {
                    "nombre": archivo,
                    "url": url_base
                }

    return archivos