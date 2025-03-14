"""
Módulo para gestionar productos dentro de una sucursal.
"""

import json
import boto3
import uuid

# Inicializar el cliente de DynamoDB
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Franquicias")

def obtener_franquicia(franquicia_id):
    """Obtiene una franquicia por su ID desde DynamoDB."""
    response = table.get_item(Key={"FranquiciaID": franquicia_id})
    return response.get("Item")

def obtener_sucursal(franquicia, sucursal_id):
    """Obtiene una sucursal dentro de una franquicia por su ID."""
    return next((sucursal for sucursal in franquicia["Sucursales"] if sucursal["SucursalID"] == sucursal_id), None)

def agregar_producto_a_sucursal(sucursal, producto_id, nombre):
    """Agrega un producto a una sucursal."""
    sucursal.setdefault("Productos", []).append({
        "ProductoID": producto_id,
        "Nombre": nombre
    })

def manejar_productos(event, metodo):
    """
    Función para manejar las operaciones CRUD de productos en sucursales.
    
    Parámetros:
    - event: Dict con la información de la solicitud HTTP.
    - metodo: Método HTTP utilizado (POST).

    Retorna:
    - Dict con el código de estado y el cuerpo de la respuesta.
    """
    
    if metodo != "POST":
        return {"statusCode": 405, "body": json.dumps({"error": "Método no permitido"})}

    data = event.get("queryStringParameters", {})

    # Validar parámetros obligatorios
    required_params = ["franquicia_id", "sucursal_id", "nombre"]
    if not all(param in data for param in required_params):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Faltan parámetros 'franquicia_id', 'sucursal_id' o 'nombre'"})
        }

    franquicia_id, sucursal_id, nombre = data["franquicia_id"], data["sucursal_id"], data["nombre"]

    # Obtener la franquicia
    franquicia = obtener_franquicia(franquicia_id)
    if not franquicia:
        return {"statusCode": 404, "body": json.dumps({"error": "Franquicia no encontrada"})}

    # Obtener la sucursal
    sucursal = obtener_sucursal(franquicia, sucursal_id)
    if not sucursal:
        return {"statusCode": 404, "body": json.dumps({"error": "Sucursal no encontrada"})}

    # Agregar producto
    producto_id = str(uuid.uuid4())
    agregar_producto_a_sucursal(sucursal, producto_id, nombre)

    # Guardar cambios en la base de datos
    table.put_item(Item=franquicia)

    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Producto creado", "ProductoID": producto_id})
    }
