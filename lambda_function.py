import json
from handlers.franquicias import manejar_franquicias
from handlers.sucursales import manejar_sucursales
from handlers.productos import manejar_productos

def lambda_handler(event, context):
    """Manejador principal de la API Lambda"""

    # Extraer valores con manejo de errores
    ruta = event.get("resource", "")  # Cambiado de "path" a "resource"
    metodo = event.get("httpMethod", "").upper()

    # Log de depuración
    print(f"Evento recibido: {json.dumps(event, indent=2)}")
    print(f"Ruta recibida: {ruta}, Método recibido: {metodo}")

    # Lista de métodos permitidos
    metodos_permitidos = {"GET", "POST", "PUT", "DELETE"}

    if metodo not in metodos_permitidos:
        return {"statusCode": 400, "body": json.dumps({"error": "Método no soportado."})}

    if ruta == "/":
        return {"statusCode": 200, "body": json.dumps({"message": "API funcionando correctamente"})}
    elif ruta == "/sucursales":
        return manejar_sucursales(event, metodo)
    elif ruta == "/productos":
        return manejar_productos(event, metodo)
    elif ruta == "/franquicias":
        return manejar_franquicias(event, metodo)

    return {"statusCode": 404, "body": json.dumps({"error": "Ruta no encontrada"})}
