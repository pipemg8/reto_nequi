"""
Módulo de servicio para la gestión de franquicias en DynamoDB.
"""

import json
import uuid
from typing import Optional, Dict, Any
from repositories.dynamo_repository import DynamoRepository


class FranquiciaService:
    """Servicio para manejar operaciones CRUD de franquicias con DynamoDB."""

    def __init__(self):
        self.repository = DynamoRepository("Franquicias")

    def franquicia_existe(self, franquicia_id: str) -> bool:
        """Verifica si una franquicia con el ID dado existe en la base de datos."""
        return self.repository.get_item({"FranquiciaID": franquicia_id}) is not None

    def crear_franquicia(self, nombre: str) -> Dict[str, Any]:
        """Crea una nueva franquicia en la base de datos."""
        if not nombre:
            return self._response(400, "El parámetro 'nombre' es obligatorio.")

        nueva_franquicia = {
            "FranquiciaID": str(uuid.uuid4()),
            "Nombre": nombre,
            "Sucursales": []
        }

        try:
            self.repository.put_item(nueva_franquicia)
            return self._response(201, "Franquicia creada exitosamente.", nueva_franquicia)
        except Exception as e:
            return self._response(500, f"Error al crear franquicia: {str(e)}")

    def obtener_franquicia(self, franquicia_id: str) -> Dict[str, Any]:
        """Obtiene una franquicia por ID."""
        if not franquicia_id:
            return self._response(400, "Se requiere el parámetro 'franquicia_id'.")

        franquicia = self.repository.get_item({"FranquiciaID": franquicia_id})
        if not franquicia:
            return self._response(404, "Franquicia no encontrada.")

        return self._response(200, "Franquicia encontrada.", franquicia)

    def actualizar_franquicia(self, franquicia_id: str, nuevo_nombre: str) -> Dict[str, Any]:
        """Actualiza el nombre de una franquicia existente."""
        if not franquicia_id or not nuevo_nombre:
            return self._response(400, "Se requieren 'franquicia_id' y 'nuevo_nombre'.")

        if not self.franquicia_existe(franquicia_id):
            return self._response(404, "La franquicia no existe.")

        try:
            self.repository.update_item(
                {"FranquiciaID": franquicia_id},
                "SET Nombre = :nombre",
                {":nombre": nuevo_nombre}
            )
            return self._response(200, "Franquicia actualizada.")
        except Exception as e:
            return self._response(500, f"Error al actualizar franquicia: {str(e)}")

    def eliminar_franquicia(self, franquicia_id: str) -> Dict[str, Any]:
        """Elimina una franquicia por su ID."""
        if not franquicia_id:
            return self._response(400, "Se requiere el parámetro 'franquicia_id'.")

        if not self.franquicia_existe(franquicia_id):
            return self._response(404, "La franquicia no existe.")

        try:
            self.repository.delete_item({"FranquiciaID": franquicia_id})
            return self._response(200, "Franquicia eliminada.")
        except Exception as e:
            return self._response(500, f"Error al eliminar franquicia: {str(e)}")

    @staticmethod
    def _response(status_code: int, message: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Genera una respuesta HTTP estándar."""
        response_body = {"message": message}
        if data:
            response_body["data"] = data
        return {"statusCode": status_code, "body": json.dumps(response_body)}
