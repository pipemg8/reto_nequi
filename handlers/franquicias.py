import services.franquicia_service as franquicia_service
import json

def manejar_franquicias(event, context, service=None):
    """Manejador para franquicias"""

    # Inyección de dependencia para facilitar pruebas (si no se pasa un servicio, se instancia uno)
    service = service or franquicia_service.FranquiciaService()

    http_method = event.get("httpMethod", "").upper()
    params = event.get("queryStringParameters", {}) or {}

    print(f"📌 Método recibido: {http_method}, Parámetros: {json.dumps(params)}")

    # Mapeo de métodos HTTP a funciones del servicio
    handlers = {
        "GET": lambda: validar_y_ejecutar(service.obtener_franquicia, params, ["franquicia_id"]),
        "POST": lambda: validar_y_ejecutar(service.crear_franquicia, params, ["nombre"]),
        "PUT": lambda: validar_y_ejecutar(service.actualizar_franquicia, params, ["id", "nombre"]),
        "DELETE": lambda: validar_y_ejecutar(service.eliminar_franquicia, params, ["id"])
    }

    # Ejecutar el manejador correspondiente o retornar error si el método no está soportado
    return handlers.get(http_method, lambda: {"statusCode": 400, "body": json.dumps({"error": "Método no soportado."})})()

def validar_y_ejecutar(func, params, required_params):
    """Valida que los parámetros requeridos estén presentes y ejecuta la función"""
    if not all(param in params and params[param] for param in required_params):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Faltan parámetros obligatorios: {', '.join(required_params)}"})
        }

    # Ejecutar la función con los parámetros requeridos
    resultado = func(*[params[param] for param in required_params])

    # Si la función devuelve un diccionario, aseguramos que sea serializable
    if isinstance(resultado, dict):
        return {"statusCode": 200, "body": json.dumps(resultado)}

    return resultado
