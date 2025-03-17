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
            logger.info(f"✅ Ítem insertado correctamente: {json.dumps(item, indent=2)}")
            return True
        except (ClientError, BotoCoreError) as e:
            logger.error(f"❌ Error al insertar ítem en DynamoDB: {str(e)}")
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

    def actualizar_franquicia(self, franquicia_id: str, nuevo_nombre: str) -> bool:
        """Actualiza el nombre de una franquicia en DynamoDB."""
        try:
            resultado = self.update_item(
                key={"FranquiciaID": franquicia_id},
                update_expression="SET Nombre = :nuevo_nombre",
                expression_values={":nuevo_nombre": nuevo_nombre}
            )

            if resultado:
                logger.info(f"✅ Franquicia {franquicia_id} actualizada correctamente a '{nuevo_nombre}'.")
                return True
            else:
                logger.warning(f"⚠️ No se pudo actualizar la franquicia {franquicia_id}.")
                return False

        except ClientError as e:
            logger.error(f"❌ Error al actualizar franquicia: {e.response['Error']['Message']}")
            return False
        except BotoCoreError as e:
            logger.error(f"❌ Error al actualizar franquicia (BotoCoreError): {str(e)}")
            return False

    def actualizar_sucursal(self, franquicia_id: str, sucursal_id: str, nuevo_nombre: str) -> bool:
        """Actualiza el nombre de una sucursal dentro de una franquicia en DynamoDB."""
        try:
            # Obtener la franquicia
            franquicia = self.get_item({"FranquiciaID": franquicia_id})
            if not franquicia:
                logger.warning(f"⚠️ Franquicia {franquicia_id} no encontrada.")
                return False

            sucursales = franquicia.get("Sucursales", [])
            index = next((i for i, s in enumerate(sucursales) if s["SucursalID"] == sucursal_id), -1)

            if index == -1:
                logger.warning(f"⚠️ Sucursal {sucursal_id} no encontrada en la franquicia {franquicia_id}.")
                return False

            # Actualizar el nombre de la sucursal en la posición específica
            update_expression = f"SET Sucursales[{index}].Nombre = :nuevo_nombre"
            expression_values = {":nuevo_nombre": nuevo_nombre}

            resultado = self.update_item(
                key={"FranquiciaID": franquicia_id},
                update_expression=update_expression,
                expression_values=expression_values
            )

            if resultado:
                logger.info(f"✅ Sucursal {sucursal_id} actualizada correctamente a '{nuevo_nombre}'.")
                return True
            else:
                logger.warning(f"⚠️ No se pudo actualizar la sucursal {sucursal_id}.")
                return False

        except ClientError as e:
            logger.error(f"❌ Error al actualizar sucursal: {e.response['Error']['Message']}")
            return False
        except BotoCoreError as e:
            logger.error(f"❌ Error al actualizar sucursal (BotoCoreError): {str(e)}")
            return False

# ✅ Función para manejar solicitudes de franquicias en Lambda
def manejar_franquicias(event, context):
    """Maneja las solicitudes de franquicias desde API Gateway."""
    logger.info(f"📩 Evento recibido: {json.dumps(event)}")

    repo = DynamoRepository(table_name="Franquicias")

    http_method = event.get("httpMethod")
    query_params = event.get("queryStringParameters", {})

    if http_method == "GET":
        franquicia_id = query_params.get("franquicia_id")
        if not franquicia_id:
            return {"statusCode": 400, "body": json.dumps({"error": "Falta el parámetro franquicia_id"})}
        
        franquicia = repo.get_item({"FranquiciaID": franquicia_id})
        if franquicia:
            return {"statusCode": 200, "body": json.dumps(franquicia)}
        else:
            return {"statusCode": 404, "body": json.dumps({"error": "Franquicia no encontrada"})}

    return {"statusCode": 405, "body": json.dumps({"error": "Método no permitido"})}
