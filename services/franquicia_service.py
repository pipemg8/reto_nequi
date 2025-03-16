import json
import uuid
from http import HTTPStatus
from typing import Dict, Any, Optional
from repositories.dynamo_repository import DynamoRepository
from services.sucursal_service import SucursalService

class ProductoService:
    """Servicio para gestionar productos en sucursales."""
    
    def __init__(self, repositorio: DynamoRepository):
        self.repositorio = repositorio
        self.sucursal_service = SucursalService()

    def agregar_producto(self, franquicia_id: str, sucursal_id: str, nombre: str) -> Dict[str, Any]:
        """
        Agrega un producto a una sucursal específica de una franquicia.
        """
        if not all([franquicia_id, sucursal_id, nombre]):
            return self._response(HTTPStatus.BAD_REQUEST, "Se requieren 'franquicia_id', 'sucursal_id' y 'nombre'.")

        franquicia = self.sucursal_service.obtener_franquicia(franquicia_id)
        if not franquicia:
            return self._response(HTTPStatus.NOT_FOUND, "Franquicia no encontrada.")

        sucursal = self.sucursal_service.obtener_sucursal(franquicia, sucursal_id)
        if not sucursal:
            return self._response(HTTPStatus.NOT_FOUND, "Sucursal no encontrada.")

        producto_id = str(uuid.uuid4())
        sucursal.setdefault("Productos", []).append({
            "ProductoID": producto_id,
            "Nombre": nombre
        })

        try:
            self.sucursal_service.actualizar_franquicia(franquicia_id, franquicia["Sucursales"])
            return self._response(HTTPStatus.CREATED, "Producto agregado exitosamente.", {"ProductoID": producto_id})
        except Exception as e:
            return self._response(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error al agregar producto: {str(e)}")

    def eliminar_producto(self, franquicia_id: str, sucursal_id: str, producto_id: str) -> Dict[str, Any]:
        """
        Elimina un producto de una sucursal específica.
        """
        if not all([franquicia_id, sucursal_id, producto_id]):
            return self._response(HTTPStatus.BAD_REQUEST, "Se requieren 'franquicia_id', 'sucursal_id' y 'producto_id'.")

        franquicia = self.sucursal_service.obtener_franquicia(franquicia_id)
        if not franquicia:
            return self._response(HTTPStatus.NOT_FOUND, "Franquicia no encontrada.")

        sucursal = self.sucursal_service.obtener_sucursal(franquicia, sucursal_id)
        if not sucursal:
            return self._response(HTTPStatus.NOT_FOUND, "Sucursal no encontrada.")

        productos = sucursal.get("Productos", [])
        nuevo_productos = [p for p in productos if p["ProductoID"] != producto_id]

        if len(nuevo_productos) == len(productos):
            return self._response(HTTPStatus.NOT_FOUND, "Producto no encontrado.")

        sucursal["Productos"] = nuevo_productos

        try:
            self.sucursal_service.actualizar_franquicia(franquicia_id, franquicia["Sucursales"])
            return self._response(HTTPStatus.OK, "Producto eliminado exitosamente.")
        except Exception as e:
            return self._response(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error al eliminar producto: {str(e)}")

    @staticmethod
    def _response(status_code: int, message: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Genera una respuesta estándar."""
        response_body = {"message": message}
        if data:
            response_body["data"] = data
        return {"statusCode": status_code, "body": json.dumps(response_body)}
