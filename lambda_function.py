import json
from handlers.franquicias import manejar_franquicias
from handlers.sucursales import manejar_sucursales
from handlers.productos import manejar_productos

def lambda_handler(event, context):
    """Manejador principal de la API Lambda"""

    # Extraer valores con manejo de errores
    ruta = event.get("path", "")
    metodo = event.get("httpMethod", "").upper()  # Convertir método a mayúsculas

    # Log de depuración
    print(f"Evento recibido: {json.dumps(event, indent=2)}")
    print(f"Ruta recibida: {ruta}, Método recibido: {metodo}")

    # Lista de métodos permitidos
    metodos_permitidos = {"GET", "POST", "PUT", "DELETE"}

    if metodo not in metodos_permitidos:
        return {"statusCode": 400, "body": json.dumps({"error": "Método no soportado."})}

    if ruta == "/":
        return {"statusCode": 200, "body": json.dumps({"message": "API funcionando correctamente"})}
    elif "/sucursales" in ruta:
        return manejar_sucursales(event, metodo)
    elif "/productos" in ruta:
        return manejar_productos(event, metodo)
    elif "/franquicias" in ruta:
        return manejar_franquicias(event, metodo)

    return {"statusCode": 404, "body": json.dumps({"error": "Ruta no encontrada"})}
