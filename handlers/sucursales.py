import json
import uuid
import logging
from http import HTTPStatus
from services.sucursal_service import SucursalService
from repositories.dynamo_repository import DynamoRepository

# Configurar logs
logging.basicConfig(level=logging.INFO)

# Inicializar servicio de sucursales
franquicia_repo = DynamoRepository("Franquicias")
sucursal_service = SucursalService(franquicia_repo)

def manejar_sucursales(event, context):
    """Maneja operaciones CRUD para sucursales dentro de franquicias."""
    logging.info(f"📌 Evento recibido: {json.dumps(event)}")

    metodo = event.get("httpMethod", "").upper()
    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}

    franquicia_id = path_params.get("franquicia_id") or query_params.get("franquicia_id")

    handlers = {
        "GET": lambda: obtener_sucursales(franquicia_id),
        "POST": lambda: crear_sucursal(franquicia_id, event),
        "PUT": lambda: actualizar_sucursal(franquicia_id, event),
        "DELETE": lambda: eliminar_sucursal(franquicia_id, event)
    }

    if metodo == "POST" and not franquicia_id:
        return crear_franquicia_con_sucursal(event)

    if not franquicia_id:
        return response_json(HTTPStatus.BAD_REQUEST, {"error": "Se requiere 'franquicia_id'"})

    return handlers.get(metodo, metodo_no_soportado)()

def obtener_body(event):
    """Obtiene y valida el cuerpo de la solicitud HTTP."""
    try:
        return json.loads(event.get("body", "{}")) if event.get("body") else {}
    except json.JSONDecodeError:
        return {}

def crear_franquicia_con_sucursal(event):
    """Crea una nueva franquicia con su primera sucursal."""
    body = obtener_body(event)

    if not all(k in body for k in ["nombre_franquicia", "nombre_sucursal"]):
        return response_json(HTTPStatus.BAD_REQUEST, {"error": "Se requieren 'nombre_franquicia' y 'nombre_sucursal'"})

    return sucursal_service.crear_franquicia_con_sucursal(body["nombre_franquicia"], body["nombre_sucursal"])

def obtener_sucursales(franquicia_id):
    """Obtiene las sucursales de una franquicia."""
    return sucursal_service.obtener_sucursales(franquicia_id)

def crear_sucursal(franquicia_id, event):
    """Crea una nueva sucursal en una franquicia."""
    body = obtener_body(event)
    nombre_sucursal = body.get("nombre") or body.get("nombre_sucursal")

    if not nombre_sucursal:
        return response_json(HTTPStatus.BAD_REQUEST, {"error": "Se requiere el parámetro 'nombre' o 'nombre_sucursal'"})

    return sucursal_service.agregar_sucursal(franquicia_id, nombre_sucursal)

def actualizar_sucursal(franquicia_id, event):
    """Actualiza el nombre de una sucursal existente."""
    body = obtener_body(event)

    if not all(k in body for k in ["sucursal_id", "nombre"]):
        return response_json(HTTPStatus.BAD_REQUEST, {"error": "Se requieren 'sucursal_id' y 'nombre'"})

    return sucursal_service.actualizar_sucursal(franquicia_id, body["sucursal_id"], body["nombre"])

def eliminar_sucursal(franquicia_id, event):
    """Elimina una sucursal de una franquicia."""
    body = obtener_body(event)

    if "sucursal_id" not in body:
        return response_json(HTTPStatus.BAD_REQUEST, {"error": "Falta el parámetro 'sucursal_id'"})

    return sucursal_service.eliminar_sucursal(franquicia_id, body["sucursal_id"])

def response_json(status_code, body):
    """Genera una respuesta HTTP estándar."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }

def metodo_no_soportado():
    """Respuesta para métodos HTTP no permitidos."""
    return response_json(HTTPStatus.METHOD_NOT_ALLOWED, {"error": "Método no permitido"})
