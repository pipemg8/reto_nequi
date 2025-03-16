import json
import uuid
from typing import Optional, Dict, Any
from repositories.dynamo_repository import DynamoRepository  # Uso correcto del repositorio

class FranquiciaService:
    """Servicio para manejar operaciones CRUD de franquicias."""

    def __init__(self, repository=None):
        """Inicializa el servicio con un repositorio externo, o usa DynamoDB por defecto."""
        self.repository = repository or DynamoRepository("Franquicias")

    def franquicia_existe(self, franquicia_id: str) -> bool:
        """Verifica si una franquicia con el ID dado existe en el repositorio."""
        return self.repository.get_item({"FranquiciaID": franquicia_id}) is not None

    def crear_franquicia(self, nombre: str) -> Dict[str, Any]:
        """Crea una nueva franquicia."""
        self._validar_nombre(nombre)

        nueva_franquicia = {
            "FranquiciaID": str(uuid.uuid4()),
            "Nombre": nombre,
            "Sucursales": []
        }
        
        try:
            self.repository.put_item(nueva_franquicia)
            return self._response(201, "Franquicia creada correctamente.", nueva_franquicia)
        except Exception as e:
            return self._response(500, f"Error al crear franquicia: {str(e)}")

    def obtener_franquicia(self, franquicia_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una franquicia por su ID."""
        return self.repository.get_item({"FranquiciaID": franquicia_id})

    def actualizar_franquicia(self, franquicia_id: str, nuevo_nombre: str) -> Dict[str, Any]:
        """Actualiza el nombre de una franquicia."""
        self._validar_nombre(nuevo_nombre)

        if not self.franquicia_existe(franquicia_id):
            return self._response(404, "Franquicia no encontrada.")

        try:
            self.repository.update_item(
                {"FranquiciaID": franquicia_id},
                "SET Nombre = :nombre",
                {":nombre": nuevo_nombre}
            )
            return self._response(200, "Franquicia actualizada correctamente.")
        except Exception as e:
            return self._response(500, f"Error al actualizar franquicia: {str(e)}")

    def eliminar_franquicia(self, franquicia_id: str) -> Dict[str, Any]:
        """Elimina una franquicia por su ID."""
        if not self.franquicia_existe(franquicia_id):
            return self._response(404, "Franquicia no encontrada.")

        try:
            self.repository.delete_item({"FranquiciaID": franquicia_id})
            return self._response(200, "Franquicia eliminada correctamente.")
        except Exception as e:
            return self._response(500, f"Error al eliminar franquicia: {str(e)}")

    def actualizar_sucursales(self, franquicia_id: str, sucursales: list) -> Dict[str, Any]:
        """Actualiza la lista de sucursales de una franquicia."""
        if not self.franquicia_existe(franquicia_id):
            return self._response(404, "Franquicia no encontrada.")

        try:
            self.repository.update_item(
                {"FranquiciaID": franquicia_id},
                "SET Sucursales = :sucursales",
                {":sucursales": sucursales}
            )
            return self._response(200, "Sucursales actualizadas correctamente.")
        except Exception as e:
            return self._response(500, f"Error al actualizar sucursales: {str(e)}")

    @staticmethod
    def _validar_nombre(nombre: str):
        """Valida que el nombre no esté vacío."""
        if not nombre or not nombre.strip():
            raise ValueError("El parámetro 'nombre' es obligatorio.")

    @staticmethod
    def _response(status_code: int, message: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Genera una respuesta estándar."""
        response_body = {"message": message}
        if data:
            response_body["data"] = data
        return {"statusCode": status_code, "body": json.dumps(response_body)}
