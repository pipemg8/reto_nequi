import json
from handlers.franquicias import manejar_franquicias
from handlers.sucursales import manejar_sucursales
from handlers.productos import manejar_productos

def lambda_handler(event, context):
    """Manejador principal de la API Lambda"""

    ruta = event.get("resource", "").strip()  # Asegurar limpieza de la ruta
    metodo = str(event.get("httpMethod", "")).strip().upper()  # Limpiar y convertir método

    # Logs para depuración
    print(f"Evento recibido: {json.dumps(event, indent=2)}")
    print(f"Ruta recibida: {ruta}, Método recibido: {metodo}")

    # Métodos permitidos
    metodos_permitidos = {"GET", "POST", "PUT", "DELETE"}
    print(f"Lista de métodos permitidos: {metodos_permitidos}")

    # Validar método HTTP
    if metodo not in metodos_permitidos:
        print(f"ERROR: Método '{metodo}' no permitido. Métodos válidos: {metodos_permitidos}")
        return {"statusCode": 400, "body": json.dumps({"error": "Método no soportado."})}

    # Manejo de rutas
    if ruta == "/":
        return {"statusCode": 200, "body": json.dumps({"message": "API funcionando correctamente"})}
    elif ruta == "/sucursales":
        return manejar_sucursales(event, metodo)
    elif ruta == "/productos":
        return manejar_productos(event, metodo)
    elif ruta == "/franquicias":
        return manejar_franquicias(event, metodo)

    # Si la ruta no se encuentra
    return {"statusCode": 404, "body": json.dumps({"error": "Ruta no encontrada"})}
