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
        return {"statusCode": 400, "body": json.dumps({"error": "Falta el parámetro 'franquicia_id'"})}

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
        return {"statusCode": 400, "body": json.dumps({"error": "Faltan parámetros 'franquicia_id' o 'nombre'"})}

    franquicia_id = data["franquicia_id"]
    sucursal_id = str(uuid.uuid4())

    response = table.get_item(Key={"FranquiciaID": franquicia_id})

    if "Item" not in response:
        return {"statusCode": 404, "body": json.dumps({"error": "Franquicia no encontrada"})}

    franquicia = response["Item"]
    if "Sucursales" not in franquicia:
        franquicia["Sucursales"] = []

    franquicia["Sucursales"].append({"SucursalID": sucursal_id, "Nombre": data["nombre"]})

    table.put_item(Item=franquicia)  # Guardar cambios en la BD

    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Sucursal creada", "SucursalID": sucursal_id})
    }

def actualizar_sucursal(event):
    """ Actualiza el nombre de una sucursal existente. """
    data = event.get("queryStringParameters", {})

    if not data or "franquicia_id" not in data or "sucursal_id" not in data or "nombre" not in data:
        return {"statusCode": 400, "body": json.dumps({"error": "Faltan parámetros 'franquicia_id', 'sucursal_id' o 'nombre'"})}

    franquicia_id = data["franquicia_id"]
    sucursal_id = data["sucursal_id"]
    nuevo_nombre = data["nombre"]

    response = table.get_item(Key={"FranquiciaID": franquicia_id})

    if "Item" not in response:
        return {"statusCode": 404, "body": json.dumps({"error": "Franquicia no encontrada"})}

    franquicia = response["Item"]
    sucursales = franquicia.get("Sucursales", [])

    # Buscar la sucursal específica
    for sucursal in sucursales:
        if sucursal["SucursalID"] == sucursal_id:
            sucursal["Nombre"] = nuevo_nombre
            break
    else:
        return {"statusCode": 404, "body": json.dumps({"error": "Sucursal no encontrada"})}

    # Guardar el cambio usando update_item en DynamoDB
    table.update_item(
        Key={"FranquiciaID": franquicia_id},
        UpdateExpression="SET Sucursales = :s",
        ExpressionAttributeValues={":s": sucursales}
    )

    return {"statusCode": 200, "body": json.dumps({"message": "Sucursal actualizada"})}

def eliminar_sucursal(event):
    """ Elimina una sucursal de una franquicia. """
    data = event.get("queryStringParameters", {})

    if not data or "franquicia_id" not in data or "sucursal_id" not in data:
        return {"statusCode": 400, "body": json.dumps({"error": "Faltan parámetros 'franquicia_id' o 'sucursal_id'"})}

    franquicia_id = data["franquicia_id"]
    sucursal_id = data["sucursal_id"]

    response = table.get_item(Key={"FranquiciaID": franquicia_id})

    if "Item" not in response:
        return {"statusCode": 404, "body": json.dumps({"error": "Franquicia no encontrada"})}

    franquicia = response["Item"]
    sucursales = franquicia.get("Sucursales", [])

    # Filtrar las sucursales para eliminar la indicada
    nuevas_sucursales = [s for s in sucursales if s["SucursalID"] != sucursal_id]

    if len(nuevas_sucursales) == len(sucursales):
        return {"statusCode": 404, "body": json.dumps({"error": "Sucursal no encontrada"})}

    # Guardar los cambios en DynamoDB
    table.update_item(
        Key={"FranquiciaID": franquicia_id},
        UpdateExpression="SET Sucursales = :s",
        ExpressionAttributeValues={":s": nuevas_sucursales}
    )

    return {"statusCode": 200, "body": json.dumps({"message": "Sucursal eliminada"})}
