import json
import boto3
import uuid

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Franquicias")

def manejar_franquicias(event, metodo):
    """
    Manejador principal de las operaciones sobre franquicias.
    Soporta operaciones GET, POST, PUT y DELETE.
    """
    
    if metodo == "GET":
        return obtener_franquicia(event)
    elif metodo == "POST":
        return crear_franquicia(event)
    elif metodo == "PUT":
        return actualizar_franquicia(event)
    elif metodo == "DELETE":
        return eliminar_franquicia(event)
    
    return {"statusCode": 405, "body": json.dumps({"error": "Método no permitido"})}

def crear_franquicia(event):
    """
    Crea una nueva franquicia en la base de datos.
    """
    data = event.get("queryStringParameters", {})
    if not data or "nombre" not in data:
        return {"statusCode": 400, "body": json.dumps({"error": "Falta el parámetro 'nombre' en la query string"})}
    
    franquicia_id = str(uuid.uuid4())
    item = {
        "FranquiciaID": franquicia_id,
        "Nombre": data["nombre"],
        "Sucursales": []
    }
    
    table.put_item(Item=item)
    return {"statusCode": 201, "body": json.dumps({"message": "Franquicia creada", "FranquiciaID": franquicia_id})}

def obtener_franquicia(event):
    """
    Obtiene la información de una franquicia específica si se proporciona un ID,
    o devuelve todas las franquicias si no se proporciona un ID.
    """
    params = event.get("queryStringParameters", {})
    franquicia_id = params.get("id")
    
    if franquicia_id:
        response = table.get_item(Key={"FranquiciaID": franquicia_id})
        if "Item" in response:
            return {"statusCode": 200, "body": json.dumps(response["Item"])}
        return {"statusCode": 404, "body": json.dumps({"error": "Franquicia no encontrada"})}
    
    response = table.scan()
    return {"statusCode": 200, "body": json.dumps(response.get("Items", []))}

def actualizar_franquicia(event):
    """
    Actualiza el nombre de una franquicia existente.
    """
    params = event.get("queryStringParameters", {})
    franquicia_id = params.get("id")
    nuevo_nombre = params.get("nombre")
    
    if not franquicia_id or not nuevo_nombre:
        return {"statusCode": 400, "body": json.dumps({"error": "Se requieren 'id' y 'nombre' en la query string"})}
    
    response = table.update_item(
        Key={"FranquiciaID": franquicia_id},
        UpdateExpression="SET Nombre = :nombre",
        ExpressionAttributeValues={":nombre": nuevo_nombre},
        ReturnValues="UPDATED_NEW"
    )
    
    return {"statusCode": 200, "body": json.dumps({"message": "Franquicia actualizada"})}

def eliminar_franquicia(event):
    """
    Elimina una franquicia de la base de datos.
    """
    params = event.get("queryStringParameters", {})
    franquicia_id = params.get("id")
    
    if not franquicia_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Se requiere el parámetro 'id' en la query string"})}
    
    table.delete_item(Key={"FranquiciaID": franquicia_id})
    return {"statusCode": 200, "body": json.dumps({"message": "Franquicia eliminada"})}
