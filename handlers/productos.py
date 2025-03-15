"""
Módulo de handler para gestionar las rutas de productos.
"""

import json
from http import HTTPStatus
from services.producto_service import ProductoService

producto_service = ProductoService()

def response_json(status, message):
    """Genera una respuesta JSON estándar."""
    return {"statusCode": status, "body": json.dumps(message)}

def manejar_productos(event, metodo):
    """
    Maneja las operaciones de productos dentro de sucursales.

    Parámetros:
    - event: Dict con la información de la solicitud HTTP.
    - metodo: Método HTTP utilizado (POST).

    Retorna:
    - Dict con el código de estado y el cuerpo de la respuesta.
    """
    if metodo == "POST":
        return agregar_producto_handler(event)

    return response_json(HTTPStatus.METHOD_NOT_ALLOWED, {"error": "Método no permitido"})

def agregar_producto_handler(event):
    """Maneja la adición de productos a una sucursal."""
    data = event.get("queryStringParameters", {})

    required_params = ["franquicia_id", "sucursal_id", "nombre"]
    if not all(param in data for param in required_params):
        return response_json(HTTPStatus.BAD_REQUEST, {"error": "Faltan parámetros requeridos"})

    franquicia_id, sucursal_id, nombre = data["franquicia_id"], data["sucursal_id"], data["nombre"]
    
    resultado, status_code = producto_service.agregar_producto(franquicia_id, sucursal_id, nombre)
    return response_json(status_code, resultado)
