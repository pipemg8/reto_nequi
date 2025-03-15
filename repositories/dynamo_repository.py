"""
Módulo que abstrae las operaciones en DynamoDB.
"""

import boto3

class DynamoRepository:
    """Clase para interactuar con DynamoDB."""

    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def get_item(self, key: dict):
        """Obtiene un ítem de la tabla por su clave primaria."""
        response = self.table.get_item(Key=key)
        return response.get("Item")

    def update_item(self, key: dict, update_expression: str, expression_values: dict):
        """Actualiza un ítem en la tabla."""
        self.table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )

    def put_item(self, item: dict):
        """Inserta o actualiza un ítem en la tabla."""
        self.table.put_item(Item=item)
