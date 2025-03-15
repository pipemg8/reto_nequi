import json
import services.franquicia_service as franquicia_service

def manejar_franquicias(event, context, service=None):
    """Manejador para franquicias"""

    service = service or franquicia_service.FranquiciaService()

    http_method = event.get("httpMethod", "").upper()
    params = event.get("queryStringParameters", {}) or {}

    print(f"📌 Método recibido: {http_method}, Parámetros: {json.dumps(params)}")

    # Mapeo de métodos HTTP a funciones del servicio
    handlers = {
        "GET": lambda: validar_y_ejecutar(service.obtener_franquicia, params, ["franquicia_id"]),
        "POST": lambda: validar_y_ejecutar(service.crear_franquicia, params, ["nombre"]),
        "PUT": lambda: validar_y_ejecutar(service.actualizar_franquicia, params, ["franquicia_id", "nombre"]),
        "DELETE": lambda: validar_y_ejecutar(service.eliminar_franquicia, params, ["franquicia_id"])
    }

    response = handlers.get(http_method, metodo_no_soportado)()

    # 💡 Asegurar que el body sea un JSON string
    if isinstance(response.get("body"), dict):
        response["body"] = json.dumps(response["body"])  # Convertir body a string JSON

    return response

def validar_y_ejecutar(func, params, required_params):
    """Valida que los parámetros requeridos estén presentes y ejecuta la función"""
    if not all(param in params and params[param] for param in required_params):
        return respuesta(400, f"Faltan parámetros obligatorios: {', '.join(required_params)}")

    resultado = func(*[params[param] for param in required_params])

    # Si la función ya devuelve un diccionario con statusCode y body, lo retornamos sin cambios
    if isinstance(resultado, dict) and "statusCode" in resultado and "body" in resultado:
        return resultado

    return respuesta(200, resultado)

def metodo_no_soportado():
    """Respuesta estándar para métodos HTTP no soportados"""
    return respuesta(400, "Método no soportado.")

def respuesta(status_code, message):
    """Genera una respuesta HTTP consistente"""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({"message": message})  # Convertir a string JSON
    }
