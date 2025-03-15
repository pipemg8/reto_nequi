"""
Módulo de servicio para la gestión de sucursales dentro de franquicias.
"""

import json
from repositories.dynamo_repository import DynamoRepository
from typing import Optional, Dict, List, Any

class SucursalService:
    """Servicio para gestionar sucursales en franquicias."""

    def __init__(self):
        self.repository = DynamoRepository("Franquicias")

    def obtener_franquicia(self, franquicia_id: str) -> Optional[Dict]:
        """Obtiene una franquicia por su ID."""
        if not franquicia_id:
            return None
        return self.repository.get_item({"FranquiciaID": franquicia_id})

    def obtener_sucursal(self, franquicia: Dict, sucursal_id: str) -> Optional[Dict]:
        """Busca una sucursal dentro de una franquicia."""
        return next(
            (sucursal for sucursal in franquicia.get("Sucursales", []) if sucursal["SucursalID"] == sucursal_id),
            None
        )

    def agregar_sucursal(self, franquicia_id: str, nueva_sucursal: Dict) -> Dict[str, Any]:
        """Agrega una nueva sucursal a una franquicia."""
        if not franquicia_id or not nueva_sucursal:
            return self._response(400, "Se requieren 'franquicia_id' y 'nueva_sucursal'.")

        franquicia = self.obtener_franquicia(franquicia_id)
        if not franquicia:
            return self._response(404, "Franquicia no encontrada.")

        franquicia.setdefault("Sucursales", []).append(nueva_sucursal)
        try:
            self.actualizar_franquicia(franquicia_id, franquicia["Sucursales"])
            return self._response(201, "Sucursal agregada exitosamente.")
        except Exception as e:
            return self._response(500, f"Error al agregar sucursal: {str(e)}")

    def eliminar_sucursal(self, franquicia_id: str, sucursal_id: str) -> Dict[str, Any]:
        """Elimina una sucursal de una franquicia."""
        if not franquicia_id or not sucursal_id:
            return self._response(400, "Se requieren 'franquicia_id' y 'sucursal_id'.")

        franquicia = self.obtener_franquicia(franquicia_id)
        if not franquicia:
            return self._response(404, "Franquicia no encontrada.")

        sucursales = franquicia.get("Sucursales", [])
        nuevas_sucursales = [s for s in sucursales if s["SucursalID"] != sucursal_id]

        if len(nuevas_sucursales) == len(sucursales):
            return self._response(404, "Sucursal no encontrada.")

        try:
            self.actualizar_franquicia(franquicia_id, nuevas_sucursales)
            return self._response(200, "Sucursal eliminada exitosamente.")
        except Exception as e:
            return self._response(500, f"Error al eliminar sucursal: {str(e)}")

    def actualizar_franquicia(self, franquicia_id: str, sucursales: List[Dict]) -> None:
        """Actualiza la lista de sucursales de una franquicia en DynamoDB."""
        self.repository.update_item(
            {"FranquiciaID": franquicia_id},
            "SET Sucursales = :s",
            {":s": sucursales}
        )

    @staticmethod
    def _response(status_code: int, message: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Genera una respuesta estándar."""
        response_body = {"message": message}
        if data:
            response_body["data"] = data
        return {"statusCode": status_code, "body": json.dumps(response_body)}
