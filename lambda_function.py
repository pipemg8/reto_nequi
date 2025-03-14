import json
import boto3
import uuid

  # Inicializa el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')

  # Especifica la tabla en la que se almacenarán los datos
table = dynamodb.Table('Franquicias')

def lambda_handler(event, context):
    """
    Función principal de la Lambda que maneja las solicitudes API Gateway.
    Recibe parámetros a través de la query string en lugar del cuerpo (body).
    """

      # Extrae los parámetros de la query string, si no existen, se asigna un diccionario vacío
    data = event.get('queryStringParameters', {})

      # Verifica si el parámetro 'nombre' está presente en la query string
    if not data or 'nombre' not in data:
        return {
            "statusCode": 400,  # Código de error HTTP 400 (Bad Request)
            "body": json.dumps({"error": "Falta el parámetro 'nombre' en la query string"})
        }

      # Genera un identificador único para la nueva franquicia
    franquicia_id = str(uuid.uuid4())

      # Crea el objeto que se almacenará en DynamoDB
    item = {
        'FranquiciaID': franquicia_id,  # ID único de la franquicia
        'Nombre': data['nombre'],  # Nombre de la franquicia
        'Sucursales': []  # Lista vacía para futuras sucursales
    }

      # Inserta el objeto en la tabla de DynamoDB
    table.put_item(Item=item)

      # Retorna una respuesta exitosa con el ID de la franquicia creada
    return {
        "statusCode": 201,  # Código HTTP 201 (Created)
        "body": json.dumps({"message": "Franquicia creada", "FranquiciaID": franquicia_id})
    }
 