import boto3
import json
import uuid
from boto3.dynamodb.conditions import Key

class FranquiciaService:
    """Servicio para manejar operaciones CRUD de franquicias con DynamoDB."""

    def __init__(self, table_name="Franquicias"):
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table(table_name)

    def franquicia_existe(self, franquicia_id: str) -> bool:
        """Verifica si una franquicia con el ID dado existe en la base de datos."""
        response = self.table.get_item(Key={"FranquiciaID": franquicia_id})
        return "Item" in response

    def crear_franquicia(self, nombre: str):
        """Crea una nueva franquicia en la base de datos."""
        if not nombre:
            return self._response(400, "El parámetro 'nombre' es obligatorio.")

        nueva_franquicia = {
            "FranquiciaID": str(uuid.uuid4()),
            "Nombre": nombre,
            "Sucursales": []
        }

        try:
            self.table.put_item(Item=nueva_franquicia)
            return self._response(201, "Franquicia creada exitosamente.", nueva_franquicia)
        except Exception as e:
            return self._response(500, f"Error al crear franquicia: {str(e)}")

    def obtener_franquicia(self, franquicia_id: str):
        """Obtiene una franquicia por ID."""
        if not franquicia_id:
            return self._response(400, "Se requiere el parámetro 'franquicia_id'.")

        try:
            response = self.table.get_item(Key={"FranquiciaID": franquicia_id})
            franquicia = response.get("Item")

            if not franquicia:
                return self._response(404, "Franquicia no encontrada.")

            return self._response(200, "Franquicia encontrada.", franquicia)
        except Exception as e:
            return self._response(500, f"Error al obtener franquicia: {str(e)}")

    def actualizar_franquicia(self, franquicia_id: str, nuevo_nombre: str):
        """Actualiza el nombre de una franquicia existente."""
        if not franquicia_id or not nuevo_nombre:
            return self._response(400, "Se requieren 'franquicia_id' y 'nuevo_nombre'.")

        if not self.franquicia_existe(franquicia_id):
            return self._response(404, "La franquicia no existe.")

        try:
            self.table.update_item(
                Key={"FranquiciaID": franquicia_id},
                UpdateExpression="SET Nombre = :nombre",
                ExpressionAttributeValues={":nombre": nuevo_nombre},
                ReturnValues="UPDATED_NEW"
            )

            return self._response(200, "Franquicia actualizada.")
        except Exception as e:
            return self._response(500, f"Error al actualizar franquicia: {str(e)}")

    def eliminar_franquicia(self, franquicia_id: str):
        """Elimina una franquicia por su ID."""
        if not franquicia_id:
            return self._response(400, "Se requiere el parámetro 'franquicia_id'.")

        if not self.franquicia_existe(franquicia_id):
            return self._response(404, "La franquicia no existe.")

        try:
            self.table.delete_item(Key={"FranquiciaID": franquicia_id})
            return self._response(200, "Franquicia eliminada.")
        except Exception as e:
            return self._response(500, f"Error al eliminar franquicia: {str(e)}")

    @staticmethod
    def _response(status_code: int, message: str, data=None):
        """Genera una respuesta HTTP estándar."""
        response_body = {"message": message}
        if data:
            response_body["data"] = data
        return {"statusCode": status_code, "body": json.dumps(response_body)}
