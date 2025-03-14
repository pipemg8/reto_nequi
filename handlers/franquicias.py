import services.franquicia_service as franquicia_service

def lambda_handler(event, context, service=None):
    """Manejador para franquicias"""

    # Inyección de dependencia para facilitar pruebas (si no se pasa un servicio, se instancia uno)
    service = service or franquicia_service.FranquiciaService()

    http_method = event.get("httpMethod", "").upper()
    params = event.get("queryStringParameters", {}) or {}

    # Mapeo de métodos HTTP a funciones del servicio
    handlers = {
        "POST": lambda: validar_y_ejecutar(service.crear_franquicia, params, ["nombre"]),
        "PUT": lambda: validar_y_ejecutar(service.actualizar_franquicia, params, ["id", "nombre"]),
        "DELETE": lambda: validar_y_ejecutar(service.eliminar_franquicia, params, ["id"])
    }

    # Ejecutar el manejador correspondiente o retornar error si el método no está soportado
    return handlers.get(http_method, lambda: {"statusCode": 400, "body": "Método no soportado."})()

def validar_y_ejecutar(func, params, required_params):
    """Valida que los parámetros requeridos estén presentes y ejecuta la función"""
    if not all(param in params and params[param] for param in required_params):
        return {
            "statusCode": 400,
            "body": f"Faltan parámetros obligatorios: {', '.join(required_params)}"
        }
    return func(*[params[param] for param in required_params])
