"""
Módulo para gestionar sucursales dentro de una franquicia.
"""

import json
import boto3
import uuid

# Inicializar el cliente de DynamoDB
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Franquicias")

def manejar_sucursales(event, metodo):
    print(f"Método en sucursales: {metodo}")  # Para depuración
    
    """
    Función para manejar las operaciones CRUD de sucursales.

    Parámetros:
    - event: Dict con la información de la solicitud HTTP.
    - metodo: Método HTTP utilizado (GET, POST, PUT, DELETE).

    Retorna:
    - Dict con el código de estado y el cuerpo de la respuesta.
    """

    if metodo == "GET":
        return obtener_sucursales(event)
    elif metodo == "POST":
        return crear_sucursal(event)
    elif metodo == "PUT":
        return actualizar_sucursal(event)
    elif metodo == "DELETE":
        return eliminar_sucursal(event)
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Método no soportado en sucursales."})
        }

def obtener_sucursales(event):
    """ Obtiene todas las sucursales de una franquicia específica. """
    data = event.get("queryStringParameters", {})

    if not data or "franquicia_id" not in data:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Falta el parámetro 'franquicia_id'"})
        }

    franquicia_id = data["franquicia_id"]
    response = table.get_item(Key={"FranquiciaID": franquicia_id})

    if "Item" not in response:
        return {"statusCode": 404, "body": json.dumps({"error": "Franquicia no encontrada"})}

    sucursales = response["Item"].get("Sucursales", [])

    return {"statusCode": 200, "body": json.dumps({"sucursales": sucursales})}

def crear_sucursal(event):
    """ Crea una nueva sucursal en una franquicia existente. """
    data = event.get("queryStringParameters", {})

    if not data or "franquicia_id" not in data or "nombre" not in data:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Faltan parámetros 'franquicia_id' o 'nombre'"})
        }

    franquicia_id = data["franquicia_id"]
    sucursal_id = str(uuid.uuid4())

    response = table.get_item(Key={"FranquiciaID": franquicia_id})

    if "Item" not in response:
        return {"statusCode": 404, "body": json.dumps({"error": "Franquicia no encontrada"})}

    franquicia = response["Item"]
    if "Sucursales" not in franquicia:
        franquicia["Sucursales"] = []

    franquicia["Sucursales"].append({"SucursalID": sucursal_id, "Nombre": data["nombre"]})

    table.put_item(Item=franquicia)

    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Sucursal creada", "SucursalID": sucursal_id})
    }

def actualizar_sucursal(event):
    """ Actualiza el nombre de una sucursal existente. """
    data = event.get("queryStringParameters", {})

    if not data or "franquicia_id" not in data or "sucursal_id" not in data or "nombre" not in data:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Faltan parámetros 'franquicia_id', 'sucursal_id' o 'nombre'"})
        }

    fr
