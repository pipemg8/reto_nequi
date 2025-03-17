import boto3
import logging
import json
from decimal import Decimal
from botocore.exceptions import BotoCoreError, ClientError

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_decimal(obj):
    """Convierte objetos Decimal de DynamoDB a tipos serializables."""
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj

class DynamoRepository:
    """Clase para interactuar con DynamoDB."""

    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def get_item(self, key: dict):
        """Obtiene un ítem de la tabla por su clave primaria."""
        try:
            response = self.table.get_item(Key=key)
            item = response.get("Item")
            return convert_decimal(item) if item else None
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Error al obtener ítem de DynamoDB: {str(e)}")
            return None

    def put_item(self, item: dict):
        """Inserta un nuevo ítem en la tabla."""
        try:
            self.table.put_item(Item=item)
            logger.info(f"\u2705 Ítem insertado correctamente: {json.dumps(item, indent=2)}")
            return True
        except (ClientError, BotoCoreError) as e:
            logger.error(f"\u274c Error al insertar ítem en DynamoDB: {str(e)}")
            return False
        
    def delete_item(self, key: dict) -> bool:
        """Elimina un ítem de la tabla."""
        try:
            self.table.delete_item(Key=key)
            logger.info(f"✅ Ítem eliminado correctamente: {key}")
            return True
        except (ClientError, BotoCoreError) as e:
            logger.error(f"❌ Error al eliminar ítem de DynamoDB: {str(e)}")
            return False
        
    def actualizar_franquicia(self, franquicia_id: str, sucursales: list) -> bool:
        """Actualiza la lista de sucursales de una franquicia en la base de datos."""
        try:
            response = self.table.update_item(
            Key={"FranquiciaID": franquicia_id},
            UpdateExpression="SET Sucursales = :s",
            ExpressionAttributeValues={":s": sucursales},
            ReturnValues="UPDATED_NEW"
        )
            return "Attributes" in response
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Error al actualizar franquicia en DynamoDB: {str(e)}")
        return False

    def update_item(self, key: dict, update_expression: str, expression_values: dict):
        """Actualiza un ítem en la tabla."""
        try:
            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues="UPDATED_NEW"
            )
            return convert_decimal(response.get("Attributes", {}))
        except ClientError as e:
            logger.error(f"Error en update_item: {e.response['Error']['Message']}")
            return None
        except BotoCoreError as e:
            logger.error(f"Error en update_item (BotoCoreError): {str(e)}")
            return None
