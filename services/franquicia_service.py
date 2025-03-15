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

import json
from services.franquicia_service import FranquiciaService

def manejar_franquicias(event, context, service=None):
    """Manejador principal para la entidad franquicias."""
    
    service = service or FranquiciaService()
    http_method = event.get("httpMethod", "").upper()

    print(f"📌 Método recibido: {http_method}, Event: {json.dumps(event)}")

    if http_method == "POST":
        return manejar_creacion_franquicia(event, service)
    elif http_method == "GET":
        return manejar_obtener_franquicia(event, service)
    elif http_method == "PUT":
        return manejar_actualizar_franquicia(event, service)
    elif http_method == "DELETE":
        return manejar_eliminar_franquicia(event, service)

    return respuesta(400, {"error": "Método no soportado."})

def manejar_creacion_franquicia(event, service):
    """Maneja la creación de una franquicia desde el body del request."""
    try:
        body = json.loads(event.get("body", "{}"))
        nombre = body.get("nombre")

        if not nombre:
            return respuesta(400, {"error": "El parámetro 'nombre' es obligatorio."})

        resultado = service.crear_franquicia(nombre)
        return respuesta(201, resultado)

    except Exception as e:
        print(f"❌ Error en manejar_creacion_franquicia: {str(e)}")
        return respuesta(500, {"error": f"Error interno: {str(e)}"})

import uuid
from typing import Optional, Dict, Any
from repositories.dynamo_repository import DynamoRepository
from botocore.exceptions import BotoCoreError, ClientError

class FranquiciaService:
    """Servicio para manejar operaciones CRUD de franquicias con DynamoDB."""

    def __init__(self):
        self.repository = DynamoRepository("Franquicias")

    def franquicia_existe(self, franquicia_id: str) -> bool:
        """Verifica si una franquicia con el ID dado existe en la base de datos."""
        return self.repository.get_item({"FranquiciaID": franquicia_id}) is not None

    def crear_franquicia(self, nombre: str) -> Dict[str, Any]:
        """Crea una nueva franquicia en la base de datos."""
        self._validar_nombre(nombre)

        nueva_franquicia = {
            "FranquiciaID": str(uuid.uuid4()),
            "Nombre": nombre,
            "Sucursales": []
        }

        try:
            self.repository.put_item(nueva_franquicia)
            return {
                "status": "success",
                "message": "Franquicia creada correctamente.",
                "data": nueva_franquicia
            }
        except (ClientError, BotoCoreError) as e:
            return self._error_respuesta("Error en DynamoDB", str(e))
        except Exception as e:
            return self._error_respuesta("Error desconocido", str(e))

    @staticmethod
    def _validar_nombre(nombre: str):
        if not nombre:
            raise ValueError("El parámetro 'nombre' es obligatorio.")

    @staticmethod
    def _error_respuesta(error_tipo: str, detalle: str) -> Dict[str, Any]:
        """Genera un mensaje de error estándar."""
        return {
            "status": "error",
            "message": error_tipo,
            "detail": detalle
        }
