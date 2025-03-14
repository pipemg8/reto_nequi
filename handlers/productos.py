"""
Módulo para gestionar productos dentro de una sucursal.
"""

import json
import boto3
import uuid

# Inicializar el cliente de DynamoDB
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Franquicias")

def manejar_productos(event, metodo):
    """
    Función para manejar las operaciones CRUD de productos en sucursales.
    
    Parámetros:
    - event: Dict con la información de la solicitud HTTP.
    - metodo: Método HTTP utilizado (POST).

    Retorna:
    - Dict con el código de estado y el cuerpo de la respuesta.
    """

    if metodo == "POST":
        data = event.get("queryStringParameters", {})

        if not data or "franquicia_id" not in data or "sucursal_id" not in data or "nombre" not in data:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Faltan parámetros 'franquicia_id', 'sucursal_id' o 'nombre'"})
            }

        franquicia_id = data["franquicia_id"]
        sucursal_id = data["sucursal_id"]
        producto_id = str(uuid.uuid4())

        # Obtiene la franquicia para modificarla
        response = table.get_item(Key={"FranquiciaID": franquicia_id})

        if "Item" not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Franquicia no encontrada"})
            }

        franquicia = response["Item"]

        # Busca la sucursal dentro de la franquicia
        for sucursal in franquicia["Sucursales"]:
            if sucursal["SucursalID"] == sucursal_id:
                if "Productos" not in sucursal:
                    sucursal["Productos"] = []
                sucursal["Productos"].append({
                    "ProductoID": producto_id,
                    "Nombre": data["nombre"]
                })
                break
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Sucursal no encontrada"})
            }

        # Guarda los cambios en la base de datos
        table.put_item(Item=franquicia)

        return {
            "statusCode": 201,
            "body": json.dumps({"message": "Producto creado", "ProductoID": producto_id})
        }

    return {
        "statusCode": 405,
        "body": json.dumps({"error": "Método no permitido"})
    }
