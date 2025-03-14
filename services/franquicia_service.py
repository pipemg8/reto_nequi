import boto3
import json
import uuid
from boto3.dynamodb.conditions import Key

class FranquiciaService:
    """Servicio para manejar operaciones CRUD de franquicias."""

    def __init__(self, table_name="Franquicias"):
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table(table_name)

    def franquicia_existe(self, nombre: str) -> bool:
        """Verifica si ya existe una franquicia con el mismo nombre."""
        response = self.table.query(
            IndexName="Nombre-index",  # Asegúrate de que el índice existe
            KeyConditionExpression=Key("Nombre").eq(nombre)
        )
        return response.get("Count", 0) > 0

    def crear_franquicia(self, nombre: str):
        """Crea una nueva franquicia en la base de datos."""
        if not nombre:
            return self._response(400, "El parámetro 'nombre' es obligatorio.")

        if self.franquicia_existe(nombre):
            return self._response(400, "La franquicia ya existe.")

        nueva_franquicia = {
            "FranquiciaID": str(uuid.uuid4()),
            "Nombre": nombre,
            "Sucursales": []
        }

        self.table.put_item(Item=nueva_franquicia)
        return self._response(201, "Franquicia creada exitosamente.")

    def actualizar_franquicia(self, franquicia_id: str, nuevo_nombre: str):
        """Actualiza el nombre de una franquicia existente."""
        if not franquicia_id or not nuevo_nombre:
            return self._response(400, "Se requieren 'id' y 'nombre'.")

        self.table.update_item(
            Key={"FranquiciaID": franquicia_id},
            UpdateExpression="SET Nombre = :nombre",
            ExpressionAttributeValues={":nombre": nuevo_nombre},
            ReturnValues="UPDATED_NEW"
        )

        return self._response(200, "Franquicia actualizada.")

    def eliminar_franquicia(self, franquicia_id: str):
        """Elimina una franquicia por su ID."""
        if not franquicia_id:
            return self._response(400, "Se requiere el parámetro 'id'.")

        self.table.delete_item(Key={"FranquiciaID": franquicia_id})
        return self._response(200, "Franquicia eliminada.")

    @staticmethod
    def _response(status_code: int, message: str):
        """Genera una respuesta HTTP."""
        return {"statusCode": status_code, "body": json.dumps({"message": message})}
