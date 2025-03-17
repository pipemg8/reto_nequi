import json
import uuid
import logging
from http import HTTPStatus
from typing import Dict, Any
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

def crear_franquicia(nombre: str) -> Dict[str, Any]:
    """Crea una nueva franquicia."""
    nueva_franquicia = {
        "FranquiciaID": str(uuid.uuid4()),
        "Nombre": nombre,
        "Sucursales": []
    }
    if franquicia_repo.put_item(nueva_franquicia):
        return response_json(HTTPStatus.CREATED, {"message": "Franquicia creada correctamente.", "data": nueva_franquicia})
    return response_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Error al crear la franquicia."})

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
    """Actualiza una sucursal existente."""
    body = obtener_body(event)
    sucursal_id = body.get("sucursal_id")
    nuevo_nombre = body.get("nombre")

    if not sucursal_id or not nuevo_nombre:
        return response_json(HTTPStatus.BAD_REQUEST, {"error": "Faltan parámetros 'sucursal_id' o 'nombre'"})

    return sucursal_service.actualizar_sucursal(franquicia_id, sucursal_id, nuevo_nombre)

def eliminar_sucursal(franquicia_id, event):
    """Elimina una sucursal de una franquicia."""
    body = obtener_body(event)
    sucursal_id = body.get("sucursal_id")

    if not sucursal_id:
        return response_json(HTTPStatus.BAD_REQUEST, {"error": "Falta el parámetro 'sucursal_id'"})

    return sucursal_service.eliminar_sucursal(franquicia_id, sucursal_id)

def crear_franquicia_con_sucursal(event):
    """Crea una nueva franquicia con una sucursal."""
    body = obtener_body(event)
    nombre_franquicia = body.get("nombre_franquicia")
    datos_sucursal = body.get("sucursal")

    if not nombre_franquicia or not datos_sucursal:
        return response_json(HTTPStatus.BAD_REQUEST, {"error": "Se requieren 'nombre_franquicia' y 'sucursal'"})

    franquicia_id = str(uuid.uuid4())
    sucursal_id = str(uuid.uuid4())

    franquicia = {
        "franquicia_id": franquicia_id,
        "nombre_franquicia": nombre_franquicia,
        "sucursales": [sucursal_id]
    }

    sucursal = {
        "sucursal_id": sucursal_id,
        "franquicia_id": franquicia_id,
        **datos_sucursal
    }

    try:
        sucursal_service.crear_franquicia(franquicia)
        sucursal_service.crear_sucursal(sucursal)
        return response_json(HTTPStatus.CREATED, {"franquicia_id": franquicia_id, "sucursal_id": sucursal_id})
    except Exception as e:
        logging.error(f"Error al crear franquicia y sucursal: {e}")
        return response_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Error al crear franquicia y sucursal"})

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
