import json
from http import HTTPStatus
from services.producto_service import ProductoService

producto_service = ProductoService()

def response_json(status, message):
    """Genera una respuesta JSON estándar."""
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(message)
    }

def manejar_productos(event, context):
    """
    Maneja las operaciones CRUD de productos dentro de sucursales.

    Parámetros:
    - event: Dict con la información de la solicitud HTTP.
    - context: Contexto de AWS Lambda.

    Retorna:
    - Dict con el código de estado y el cuerpo de la respuesta.
    """
    metodo = event.get("httpMethod", "").upper()
    params = event.get("queryStringParameters", {}) or {}

    handlers = {
        "GET": lambda: validar_y_ejecutar(producto_service.obtener_producto, params, ["franquicia_id", "sucursal_id", "producto_id"]),
        "POST": lambda: validar_y_ejecutar(producto_service.agregar_producto, params, ["franquicia_id", "sucursal_id", "nombre"]),
        "PUT": lambda: validar_y_ejecutar(producto_service.actualizar_producto, params, ["franquicia_id", "sucursal_id", "producto_id", "nombre"]),
        "DELETE": lambda: validar_y_ejecutar(producto_service.eliminar_producto, params, ["franquicia_id", "sucursal_id", "producto_id"])
    }

    return handlers.get(metodo, metodo_no_soportado)()

def validar_y_ejecutar(func, params, required_params):
    """Valida parámetros requeridos y ejecuta la función."""
    if not all(param in params and params[param] for param in required_params):
        return response_json(HTTPStatus.BAD_REQUEST, {"error": f"Faltan parámetros: {', '.join(required_params)}"})

    resultado = func(*[params[param] for param in required_params])

    return response_json(HTTPStatus.OK, resultado)

def metodo_no_soportado():
    """Respuesta estándar para métodos HTTP no soportados."""
    return response_json(HTTPStatus.METHOD_NOT_ALLOWED, {"error": "Método no permitido"})
