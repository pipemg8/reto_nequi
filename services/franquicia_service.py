import json
import uuid
from typing import Optional, Dict, Any
from repositories.dynamo_repository import DynamoRepository

class FranquiciaService:
    """Servicio para manejar operaciones CRUD de franquicias."""

    def __init__(self, repository=None):
        self.repository = repository or DynamoRepository("Franquicias")

    def franquicia_existe(self, franquicia_id: str) -> bool:
        return self.repository.get_item({"FranquiciaID": franquicia_id}) is not None

    def crear_franquicia(self, nombre: str) -> Dict[str, Any]:
        self._validar_nombre(nombre)
        nueva_franquicia = {
            "FranquiciaID": str(uuid.uuid4()),
            "Nombre": nombre,
            "Sucursales": []
        }
        try:
            if self.repository.put_item(nueva_franquicia):
                return self._response(201, "Franquicia creada correctamente.", nueva_franquicia)
            return self._response(500, "Error al crear la franquicia.")
        except Exception as e:
            return self._response(500, f"Error inesperado: {str(e)}")

    def obtener_franquicia(self, franquicia_id: str) -> Dict[str, Any]:
        franquicia = self.repository.get_item({"FranquiciaID": franquicia_id})
        if not franquicia:
            return self._response(404, "Franquicia no encontrada.")
        return self._response(200, "Franquicia obtenida correctamente.", franquicia)

    def actualizar_franquicia(self, franquicia_id: str, nuevo_nombre: str) -> Dict[str, Any]:
        self._validar_nombre(nuevo_nombre)
        if not self.franquicia_existe(franquicia_id):
            return self._response(404, "Franquicia no encontrada.")
        try:
            resultado = self.repository.update_item(
                {"FranquiciaID": franquicia_id},
                "SET Nombre = :nombre",
                {":nombre": nuevo_nombre}
            )
            if resultado:
                return self._response(200, "Franquicia actualizada correctamente.")
            return self._response(500, "No se pudo actualizar la franquicia.")
        except Exception as e:
            return self._response(500, f"Error inesperado: {str(e)}")

    def eliminar_franquicia(self, franquicia_id: str) -> Dict[str, Any]:
        if not self.franquicia_existe(franquicia_id):
            return self._response(404, "Franquicia no encontrada.")
        try:
            resultado = self.repository.delete_item({"FranquiciaID": franquicia_id})
            if resultado:
                return self._response(200, "Franquicia eliminada correctamente.")
            return self._response(500, "No se pudo eliminar la franquicia.")
        except Exception as e:
            return self._response(500, f"Error inesperado: {str(e)}")

    def actualizar_sucursales(self, franquicia_id: str, sucursales: list) -> Dict[str, Any]:
        if not self.franquicia_existe(franquicia_id):
            return self._response(404, "Franquicia no encontrada.")
        try:
            resultado = self.repository.update_item(
                {"FranquiciaID": franquicia_id},
                "SET Sucursales = :sucursales",
                {":sucursales": sucursales}
            )
            if resultado:
                return self._response(200, "Sucursales actualizadas correctamente.")
            return self._response(500, "No se pudo actualizar las sucursales.")
        except Exception as e:
            return self._response(500, f"Error inesperado: {str(e)}")

    @staticmethod
    def _validar_nombre(nombre: str):
        if not nombre or not nombre.strip():
            raise ValueError("El parámetro 'nombre' es obligatorio.")

    @staticmethod
    def _response(status_code: int, message: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        response_body = {"message": message}
        if data:
            response_body["data"] = data
        return {"statusCode": status_code, "body": json.dumps(response_body)}
