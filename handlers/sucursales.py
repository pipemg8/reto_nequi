import json
import uuid
import logging
from http import HTTPStatus
from repositories.dynamo_repository import DynamoRepository

# Configurar logs para depuración
logging.basicConfig(level=logging.INFO)

# Inicializar el repositorio para la tabla de franquicias
franquicia_repo = DynamoRepository("Franquicias")

def manejar_sucursales(event, context):
    """ Punto de entrada principal para manejar solicitudes HTTP """
    logging.info(f"Evento recibido: {json.dumps(event)}")  # Log para depuración

    method = event.get("httpMethod")
    path = event.get("pathParameters", {}) or {}

    if path and "franquicia_id" in path:
        franquicia_id = path["franquicia_id"]

        if method == "GET":
            return obtener_sucursales(franquicia_id)
        elif method == "POST":
            return crear_sucursal(franquicia_id, event)
        elif method == "PUT":
            return actualizar_sucursal(franquicia_id, event)
        elif method == "DELETE":
            return eliminar_sucursal(franquicia_id, event)

    return response_json(HTTPStatus.BAD_REQUEST, {"error": "Ruta o método no soportado"})

def obtener_sucursales(franquicia_id):
    franquicia = franquicia_repo.get_item({"FranquiciaID": franquicia_id})
    if not franquicia:
        return response_json(HTTPStatus.NOT_FOUND, {"error": "Franquicia no encontrada"})
    
    sucursales = franquicia.get("Sucursales", [])
    return response_json(HTTPStatus.OK, {"sucursales": sucursales})

def crear_sucursal(franquicia_id, event):
    """ Crea una sucursal para una franquicia dada """
    body = json.loads(event.get("body", "{}"))  # Convertir body JSON a diccionario

    if "nombre" not in body:
        return response_json(HTTPStatus.BAD_REQUEST, {"error": "Falta el parámetro 'nombre'"})

    franquicia = franquicia_repo.get_item({"FranquiciaID": franquicia_id})
    if not franquicia:
        return response_json(HTTPStatus.NOT_FOUND, {"error": "Franquicia no encontrada"})

    sucursal_id = str(uuid.uuid4())
    sucursales = franquicia.get("Sucursales", [])
    sucursales.append({"SucursalID": sucursal_id, "Nombre": body["nombre"]})

    franquicia_repo.update_item(
        {"FranquiciaID": franquicia_id},
        "SET Sucursales = :s",
        {":s": sucursales}
    )

    return response_json(HTTPStatus.CREATED, {"message": "Sucursal creada", "SucursalID": sucursal_id})

def actualizar_sucursal(franquicia_id, event):
    """ Actualiza el nombre de una sucursal existente """
    body = json.loads(event.get("body", "{}"))

    if "sucursal_id" not in body or "nombre" not in body:
        return response_json(HTTPStatus.BAD_REQUEST, {"error": "Faltan parámetros 'sucursal_id' o 'nombre'"})

    franquicia = franquicia_repo.get_item({"FranquiciaID": franquicia_id})
    if not franquicia:
        return response_json(HTTPStatus.NOT_FOUND, {"error": "Franquicia no encontrada"})

    sucursales = franquicia.get("Sucursales", [])
    for sucursal in sucursales:
        if sucursal["SucursalID"] == body["sucursal_id"]:
            sucursal["Nombre"] = body["nombre"]
            break
    else:
        return response_json(HTTPStatus.NOT_FOUND, {"error": "Sucursal no encontrada"})

    franquicia_repo.update_item(
        {"FranquiciaID": franquicia_id},
        "SET Sucursales = :s",
        {":s": sucursales}
    )

    return response_json(HTTPStatus.OK, {"message": "Sucursal actualizada"})

def eliminar_sucursal(franquicia_id, event):
    """ Elimina una sucursal específica """
    body = json.loads(event.get("body", "{}"))

    if "sucursal_id" not in body:
        return response_json(HTTPStatus.BAD_REQUEST, {"error": "Falta el parámetro 'sucursal_id'"})

    franquicia = franquicia_repo.get_item({"FranquiciaID": franquicia_id})
    if not franquicia:
        return response_json(HTTPStatus.NOT_FOUND, {"error": "Franquicia no encontrada"})

    sucursales = [s for s in franquicia.get("Sucursales", []) if s["SucursalID"] != body["sucursal_id"]]

    if len(sucursales) == len(franquicia.get("Sucursales", [])):
        return response_json(HTTPStatus.NOT_FOUND, {"error": "Sucursal no encontrada"})

    franquicia_repo.update_item(
        {"FranquiciaID": franquicia_id},
        "SET Sucursales = :s",
        {":s": sucursales}
    )

    return response_json(HTTPStatus.OK, {"message": "Sucursal eliminada"})

def response_json(status_code, body):
    """ Formatea la respuesta en JSON """
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
