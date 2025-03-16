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

    def update_item(self, key: dict, update_expression: str, expression_values: dict):
        """Actualiza un ítem en la tabla."""
        try:
            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues="UPDATED_NEW"
            )
            return response.get("Attributes", {})
        except ClientError as e:
            print(f"❌ Error en update_item: {e.response['Error']['Message']}")
            return None
        except BotoCoreError as e:
            print(f"❌ Error en update_item (BotoCoreError): {str(e)}")
            return None

    def actualizar_sucursal(self, franquicia_id: str, sucursal_id: str, nuevo_nombre: str) -> bool:
        """
        Actualiza el nombre de una sucursal específica dentro de una franquicia en DynamoDB.
        """
        try:
            # 🔍 Obtener la franquicia
            franquicia = self.get_item({"FranquiciaID": franquicia_id})
            if not franquicia:
                print(f"⚠️ Franquicia {franquicia_id} no encontrada.")
                return False

            sucursales = franquicia.get("Sucursales", [])
            sucursal_encontrada = False

            # 🔄 Buscar la sucursal en la lista y actualizar su nombre
            for sucursal in sucursales:
                if sucursal["SucursalID"] == sucursal_id:
                    sucursal["Nombre"] = nuevo_nombre
                    sucursal_encontrada = True
                    break

            if not sucursal_encontrada:
                print(f"⚠️ Sucursal {sucursal_id} no encontrada en la franquicia {franquicia_id}.")
                return False

            # 📝 Sobrescribir la lista de sucursales actualizada en DynamoDB
            resultado = self.update_item(
                key={"FranquiciaID": franquicia_id},
                update_expression="SET Sucursales = :s",
                expression_values={":s": sucursales}
            )

            if resultado:
                print(f"✅ Sucursal {sucursal_id} actualizada correctamente.")
                return True
            else:
                print(f"⚠️ No se pudo actualizar la sucursal {sucursal_id}.")
                return False

        except ClientError as e:
            print(f"❌ Error al actualizar sucursal: {e.response['Error']['Message']}")
            return False
        except BotoCoreError as e:
            print(f"❌ Error al actualizar sucursal (BotoCoreError): {str(e)}")
            return False
