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
    """
    Función para manejar las operaciones CRUD de sucursales.
    
    Parámetros:
    - event: Dict con la información de la solicitud HTTP.
    - metodo: Método HTTP utilizado (GET, POST).

    Retorna:
    - Dict con el código de estado y el cuerpo de la respuesta.
    """

    if metodo == "POST":
        # Extrae los parámetros de la query string
        data = event.get("queryStringParameters", {})

        # Verifica que se envíen los parámetros necesarios
        if not data or "franquicia_id" not in data or "nombre" not in data:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Faltan parámetros 'franquicia_id' o 'nombre'"})
            }

        franquicia_id = data["franquicia_id"]
        sucursal_id = str(uuid.uuid4())

        # Obtiene la franquicia para agregar la sucursal
        response = table.get_item(Key={"FranquiciaID": franquicia_id})

        if "Item" not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Franquicia no encontrada"})
            }

        # Agregar la nueva sucursal a la lista
        franquicia = response["Item"]
        franquicia["Sucursales"].append({
            "SucursalID": sucursal_id,
            "Nombre": data["nombre"]
        })

        # Actualiza la franquicia en la base de datos
        table.put_item(Item=franquicia)

        return {
            "statusCode": 201,
            "body": json.dumps({"message": "Sucursal creada", "SucursalID": sucursal_id})
        }

    return {
        "statusCode": 405,
        "body": json.dumps({"error": "Método no permitido"})
    }
