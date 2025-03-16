import json
import uuid
from typing import Optional, Dict, Any, List
from repositories.dynamo_repository import DynamoRepository

class SucursalService:
    """Servicio para gestionar sucursales en franquicias."""

    def __init__(self, repository: DynamoRepository):
        self.repository = repository

    def obtener_franquicia(self, franquicia_id: str) -> Optional[Dict]:
        """Obtiene una franquicia por su ID."""
        return self.repository.get_item({"FranquiciaID": franquicia_id}) if franquicia_id else None

    def obtener_sucursales(self, franquicia_id: str) -> Dict[str, Any]:
        """Obtiene todas las sucursales de una franquicia."""
        franquicia = self.obtener_franquicia(franquicia_id)
        if not franquicia:
            return self._response(404, "Franquicia no encontrada.")

        return self._response(200, "Sucursales obtenidas.", {"sucursales": franquicia.get("Sucursales", [])})

    def agregar_sucursal(self, franquicia_id: str, nombre_sucursal: str) -> Dict[str, Any]:
        """Agrega una nueva sucursal a una franquicia."""
        franquicia = self.obtener_franquicia(franquicia_id)
        if not franquicia:
            return self._response(404, "Franquicia no encontrada.")

        nueva_sucursal = {"SucursalID": str(uuid.uuid4()), "Nombre": nombre_sucursal}
        franquicia.setdefault("Sucursales", []).append(nueva_sucursal)

        self.actualizar_franquicia(franquicia_id, franquicia["Sucursales"])
        return self._response(201, "Sucursal agregada exitosamente.", nueva_sucursal)

    def actualizar_sucursal(self, franquicia_id: str, sucursal_id: str, nuevo_nombre: str) -> Dict[str, Any]:
        """Actualiza el nombre de una sucursal en una franquicia."""
        if not all([franquicia_id, sucursal_id, nuevo_nombre]):
            return self._response(400, "Todos los parámetros son requeridos.")

        franquicia = self.obtener_franquicia(franquicia_id)
        if not franquicia:
            return self._response(404, "Franquicia no encontrada.")

        sucursales = franquicia.get("Sucursales", [])
        sucursal_encontrada = None

        for sucursal in sucursales:
            if sucursal["SucursalID"] == sucursal_id:
                sucursal["Nombre"] = nuevo_nombre
                sucursal_encontrada = sucursal
                break

        if not sucursal_encontrada:
            return self._response(404, "Sucursal no encontrada.")

        self.actualizar_franquicia(franquicia_id, sucursales)
        return self._response(200, "Sucursal actualizada exitosamente.", sucursal_encontrada)

    def eliminar_sucursal(self, franquicia_id: str, sucursal_id: str) -> Dict[str, Any]:
        """Elimina una sucursal de una franquicia."""
        franquicia = self.obtener_franquicia(franquicia_id)
        if not franquicia:
            return self._response(404, "Franquicia no encontrada.")

        sucursales = [s for s in franquicia.get("Sucursales", []) if s["SucursalID"] != sucursal_id]

        if len(sucursales) == len(franquicia.get("Sucursales", [])):
            return self._response(404, "Sucursal no encontrada.")

        self.actualizar_franquicia(franquicia_id, sucursales)
        return self._response(200, "Sucursal eliminada exitosamente.")

    def crear_franquicia_con_sucursal(self, nombre_franquicia: str, nombre_sucursal: str) -> Dict[str, Any]:
        """Crea una franquicia con su primera sucursal."""
        franquicia_id = str(uuid.uuid4())
        sucursal_id = str(uuid.uuid4())

        nueva_franquicia = {
            "FranquiciaID": franquicia_id,
            "Nombre": nombre_franquicia,
            "Sucursales": [{"SucursalID": sucursal_id, "Nombre": nombre_sucursal}]
        }

        self.repository.put_item(nueva_franquicia)
        return self._response(201, "Franquicia creada con sucursal.", nueva_franquicia)

    def actualizar_franquicia(self, franquicia_id: str, sucursales: List[Dict]) -> None:
        """Actualiza la lista de sucursales de una franquicia en DynamoDB."""
        self.repository.update_item({"FranquiciaID": franquicia_id}, "SET Sucursales = :s", {":s": sucursales})

    @staticmethod
    def _response(status_code: int, message: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Genera una respuesta estándar."""
        response_body = {"message": message}
        if data:
            response_body["data"] = data}
        return {"statusCode": status_code, "body": json.dumps(response_body)}
