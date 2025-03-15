"""
Módulo de servicio para la gestión de sucursales dentro de franquicias.
"""

from repositories.dynamo_repository import DynamoRepository
from typing import Optional, Dict, List

class SucursalService:
    """Servicio para gestionar sucursales en franquicias."""

    def __init__(self):
        self.repository = DynamoRepository("Franquicias")

    def obtener_franquicia(self, franquicia_id: str) -> Optional[Dict]:
        """Obtiene una franquicia por su ID."""
        franquicia = self.repository.get_item({"FranquiciaID": franquicia_id})
        if not franquicia:
            return None
        return franquicia

    def obtener_sucursal(self, franquicia: Dict, sucursal_id: str) -> Optional[Dict]:
        """Busca una sucursal dentro de una franquicia."""
        return next(
            (sucursal for sucursal in franquicia.get("Sucursales", []) if sucursal["SucursalID"] == sucursal_id),
            None
        )

    def agregar_sucursal(self, franquicia_id: str, nueva_sucursal: Dict) -> bool:
        """Agrega una nueva sucursal a una franquicia."""
        franquicia = self.obtener_franquicia(franquicia_id)
        if not franquicia:
            return False  # No se encontró la franquicia

        franquicia.setdefault("Sucursales", []).append(nueva_sucursal)
        self.actualizar_franquicia(franquicia_id, franquicia["Sucursales"])
        return True

    def eliminar_sucursal(self, franquicia_id: str, sucursal_id: str) -> bool:
        """Elimina una sucursal de una franquicia."""
        franquicia = self.obtener_franquicia(franquicia_id)
        if not franquicia:
            return False

        sucursales = franquicia.get("Sucursales", [])
        nuevas_sucursales = [s for s in sucursales if s["SucursalID"] != sucursal_id]

        if len(nuevas_sucursales) == len(sucursales):
            return False  # No se encontró la sucursal a eliminar

        self.actualizar_franquicia(franquicia_id, nuevas_sucursales)
        return True

    def actualizar_franquicia(self, franquicia_id: str, sucursales: List[Dict]) -> None:
        """Actualiza la lista de sucursales de una franquicia en DynamoDB."""
        self.repository.update_item(
            {"FranquiciaID": franquicia_id},
            "SET Sucursales = :s",
            {":s": sucursales}
        )
