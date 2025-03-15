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

    return respuesta(400, {"error": "Método no soportado."})

def manejar_creacion_franquicia(event, service):
    """Maneja la creación de una franquicia desde el body del request."""
    try:
        body = json.loads(event.get("body", "{}"))
        nombre = body.get("nombre")

        if not nombre:
            return respuesta(400, {"error": "El parámetro 'nombre' es obligatorio."})

        resultado = service.crear_franquicia(nombre)
        return respuesta(201, resultado)

    except Exception as e:
        print(f"❌ Error en manejar_creacion_franquicia: {str(e)}")
        return respuesta(500, {"error": f"Error interno: {str(e)}"})

def manejar_obtener_franquicia(event, service):
    """Maneja la obtención de una franquicia."""
    try:
        path_params = event.get("pathParameters") or {}
        query_params = event.get("queryStringParameters") or {}

        franquicia_id = path_params.get("franquicia_id") or query_params.get("franquicia_id")

        if not franquicia_id:
            return respuesta(400, {"error": "Se requiere 'franquicia_id'."})

        franquicia = service.obtener_franquicia(franquicia_id)

        if not franquicia:
            return respuesta(404, {"error": "Franquicia no encontrada."})

        return respuesta(200, franquicia)

    except Exception as e:
        print(f"❌ Error en manejar_obtener_franquicia: {str(e)}")
        return respuesta(500, {"error": f"Error interno: {str(e)}"})

def manejar_actualizar_franquicia(event, service):
    """Maneja la actualización de una franquicia usando path parameters."""
    try:
        path_params = event.get("pathParameters") or {}  
        print(f"🔍 Path Parameters recibidos: {path_params}")  
        franquicia_id = path_params.get("franquicia_id")

        body = json.loads(event.get("body", "{}"))
        nuevo_nombre = body.get("nombre")

        if not franquicia_id or not nuevo_nombre:
            return respuesta(400, {"error": "Se requieren 'franquicia_id' y 'nombre'."})

        resultado = service.actualizar_franquicia(franquicia_id, nuevo_nombre)
        return respuesta(200, resultado)

    except Exception as e:
        print(f"❌ Error en manejar_actualizar_franquicia: {str(e)}")
        return respuesta(500, {"error": f"Error interno: {str(e)}"})

def manejar_eliminar_franquicia(event, service):
    """Maneja la eliminación de una franquicia usando path parameters."""
    try:
        path_params = event.get("pathParameters") or {}  
        print(f"🔍 Path Parameters recibidos: {path_params}")  
        franquicia_id = path_params.get("franquicia_id")

        if not franquicia_id:
            return respuesta(400, {"error": "Se requiere 'franquicia_id'."})

        resultado = service.eliminar_franquicia(franquicia_id)
        return respuesta(200, resultado)

    except Exception as e:
        print(f"❌ Error en manejar_eliminar_franquicia: {str(e)}")
        return respuesta(500, {"error": f"Error interno: {str(e)}"})

def respuesta(status_code, data):
    """Genera una respuesta HTTP estándar."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data)
    }
