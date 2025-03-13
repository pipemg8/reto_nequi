import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Franquicias')

def lambda_handler(event, context):
    data = json.loads(event['body'])
    franquicia_id = str(uuid.uuid4())

    item = {
        'FranquiciaID': franquicia_id,
        'Nombre': data['nombre'],
        'Sucursales': []
    }

    table.put_item(Item=item)

    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Franquicia creada", "FranquiciaID": franquicia_id})
    }
