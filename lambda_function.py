"""
Función principal que enruta las solicitudes a los módulos correspondientes.
"""

import json
from handlers.franquicias import lambda_handler as manejar_franquicias
from handlers.sucursales import manejar_sucursales
from handlers.productos import manejar_productos

def lambda_handler(event, context):
    ruta = event.get("path", "")
    metodo = event.get("httpMethod", "")

    if ruta == "/":
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Bienvenido a la API de franquicias"})
        }
    elif ruta.startswith("/franquicias"):
        return manejar_franquicias(event, metodo)
    elif ruta.startswith("/sucursales"):
        return manejar_sucursales(event, metodo)
    elif ruta.startswith("/productos"):
        return manejar_productos(event, metodo)
    
    return {"statusCode": 404, "body": json.dumps({"error": "Ruta no encontrada"})}
