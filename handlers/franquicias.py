import json
from services.franquicia_service import FranquiciaService

def manejar_franquicias(event, context, service=None):
    """Manejador principal para la entidad franquicias."""
    
    service = service or FranquiciaService()
    http_method = event.get("httpMethod", "").upper()
    
    print(f"📌 Método recibido: {http_method}, Event: {json.dumps(event)}")

    if http_method == "POST":
        return manejar_creacion_franquicia(event, service)
    elif http_method == "GET":
        return manejar_obtener_franquicia(event, service)
    elif http_method == "PUT":
        return manejar_actualizar_franquicia(event, service)
    elif http_method == "DELETE":
        return manejar_eliminar_franquicia(event, service)

    return respuesta(400, "Método no soportado.")

def manejar_creacion_franquicia(event, service):
    """Maneja la creación de una franquicia desde el body del request."""
    try:
        body = json.loads(event.get("body", "{}"))  # Leer el body como JSON
        nombre = body.get("nombre")

        if not nombre:
            return respuesta(400, "El parámetro 'nombre' es obligatorio.")

        return service.crear_franquicia(nombre)  # Llamar a la función del servicio correctamente

    except Exception as e:
        return respuesta(500, f"Error interno: {str(e)}")

def manejar_obtener_franquicia(event, service):
    """Maneja la obtención de una franquicia."""
    params = event.get("queryStringParameters", {}) or {}
    franquicia_id = params.get("franquicia_id")

    if not franquicia_id:
        return respuesta(400, "Se requiere 'franquicia_id'.")

    return service.obtener_franquicia(franquicia_id)

def manejar_actualizar_franquicia(event, service):
    """Maneja la actualización de una franquicia."""
    try:
        body = json.loads(event.get("body", "{}"))
        franquicia_id = body.get("franquicia_id")
        nuevo_nombre = body.get("nombre")

        if not franquicia_id or not nuevo_nombre:
            return respuesta(400, "Se requieren 'franquicia_id' y 'nombre'.")

        return service.actualizar_franquicia(franquicia_id, nuevo_nombre)

    except Exception as e:
        return respuesta(500, f"Error interno: {str(e)}")

def manejar_eliminar_franquicia(event, service):
    """Maneja la eliminación de una franquicia."""
    params = event.get("queryStringParameters", {}) or {}
    franquicia_id = params.get("franquicia_id")

    if not franquicia_id:
        return respuesta(400, "Se requiere 'franquicia_id'.")

    return service.eliminar_franquicia(franquicia_id)

def respuesta(status_code, message):
    """Genera una respuesta HTTP estándar."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": message})
    }
