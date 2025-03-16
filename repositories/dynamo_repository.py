"""
Módulo que abstrae las operaciones en DynamoDB.
"""

import boto3
from botocore.exceptions import BotoCoreError, ClientError

class DynamoRepository:
    """Clase para interactuar con DynamoDB."""

    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def get_item(self, key: dict):
        """Obtiene un ítem de la tabla por su clave primaria."""
        try:
            response = self.table.get_item(Key=key)
            return response.get("Item")
        except (ClientError, BotoCoreError) as e:
            print(f"❌ Error al obtener ítem de DynamoDB: {str(e)}")
            return None

    def put_item(self, item: dict):
        """Inserta o actualiza un ítem en la tabla."""
        try:
            self.table.put_item(Item=item)
        except (ClientError, BotoCoreError) as e:
            print(f"❌ Error al insertar ítem en DynamoDB: {str(e)}")

    def update_item(self, key: dict, update_expression: str, expression_values: dict):
        """Actualiza un ítem en la tabla."""
        try:
            self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
        except (ClientError, BotoCoreError) as e:
            print(f"❌ Error al actualizar ítem en DynamoDB: {str(e)}")

    def delete_item(self, key: dict):
        """Elimina un ítem de la tabla por su clave primaria."""
        try:
            self.table.delete_item(Key=key)
        except (ClientError, BotoCoreError) as e:
            print(f"❌ Error al eliminar ítem de DynamoDB: {str(e)}")

    def actualizar_franquicia(self, franquicia_id: str, sucursales: list) -> bool:
        """Actualiza la lista de sucursales de una franquicia en DynamoDB."""
        try:
            self.update_item(
                key={"FranquiciaID": franquicia_id},
                update_expression="SET Sucursales = :s",
                expression_values={":s": sucursales}
            )
            return True
        except (ClientError, BotoCoreError) as e:
            print(f"❌ Error al actualizar franquicia en DynamoDB: {str(e)}")
            return False
