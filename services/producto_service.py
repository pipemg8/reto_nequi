import json
import uuid
from http import HTTPStatus
from typing import Dict, Any, Optional
from repositories.dynamo_repository import DynamoRepository
from services.sucursal_service import SucursalService

class ProductoService:
    """Servicio para gestionar productos en sucursales."""

    def __init__(self, repositorio: Optional[DynamoRepository] = None):
        """Inicializa el servicio con un repositorio de DynamoDB."""
        self.repositorio = repositorio or DynamoRepository("Franquicias")
        self.sucursal_service = SucursalService(self.repositorio)  # ✅ Se pasa correctamente el repositorio

    def agregar_producto(self, franquicia_id: str, sucursal_id: str, nombre: str, stock: int = 0) -> Dict[str, Any]:
        """Agrega un producto a una sucursal específica de una franquicia."""
        if not all(isinstance(param, str) and param.strip() for param in [franquicia_id, sucursal_id, nombre]) or not isinstance(stock, int):
            return self._response(HTTPStatus.BAD_REQUEST, "Parámetros inválidos: 'franquicia_id', 'sucursal_id', 'nombre' y 'stock' son obligatorios.")

        franquicia = self.repositorio.get_item({"FranquiciaID": franquicia_id})
        if not franquicia:
            return self._response(HTTPStatus.NOT_FOUND, "Franquicia no encontrada.")

        sucursal = next((s for s in franquicia.get("Sucursales", []) if s["SucursalID"] == sucursal_id), None)
        if not sucursal:
            return self._response(HTTPStatus.NOT_FOUND, "Sucursal no encontrada.")

        producto_id = str(uuid.uuid4())
        sucursal.setdefault("Productos", []).append({"ProductoID": producto_id, "Nombre": nombre, "Stock": stock})

        if self.repositorio.actualizar_franquicia(franquicia_id, franquicia["Sucursales"]):
            return self._response(HTTPStatus.CREATED, "Producto agregado exitosamente.", {"ProductoID": producto_id})
        return self._response(HTTPStatus.INTERNAL_SERVER_ERROR, "Error al actualizar franquicia en DynamoDB.")

    def actualizar_producto(self, franquicia_id: str, sucursal_id: str, producto_id: str, nombre: Optional[str] = None, stock: Optional[int] = None) -> Dict[str, Any]:
        """Actualiza los datos de un producto en una sucursal específica."""
        if not all(isinstance(param, str) and param.strip() for param in [franquicia_id, sucursal_id, producto_id]):
            return self._response(HTTPStatus.BAD_REQUEST, "Parámetros inválidos: 'franquicia_id', 'sucursal_id' y 'producto_id' son obligatorios.")

        if nombre is None and stock is None:
            return self._response(HTTPStatus.BAD_REQUEST, "Debe proporcionar al menos un parámetro para actualizar: 'nombre' o 'stock'.")

        franquicia = self.repositorio.get_item({"FranquiciaID": franquicia_id})
        if not franquicia:
            return self._response(HTTPStatus.NOT_FOUND, "Franquicia no encontrada.")

        sucursal = next((s for s in franquicia.get("Sucursales", []) if s["SucursalID"] == sucursal_id), None)
        if not sucursal:
            return self._response(HTTPStatus.NOT_FOUND, "Sucursal no encontrada.")

        producto = next((p for p in sucursal.get("Productos", []) if p["ProductoID"] == producto_id), None)
        if not producto:
            return self._response(HTTPStatus.NOT_FOUND, "Producto no encontrado.")

        if nombre:
            producto["Nombre"] = nombre
        if stock is not None:
            producto["Stock"] = stock

        if self.repositorio.actualizar_franquicia(franquicia_id, franquicia["Sucursales"]):
            return self._response(HTTPStatus.OK, "Producto actualizado exitosamente.")
        return self._response(HTTPStatus.INTERNAL_SERVER_ERROR, "Error al actualizar franquicia en DynamoDB.")

    def eliminar_producto(self, franquicia_id: str, sucursal_id: str, producto_id: str) -> Dict[str, Any]:
        """Elimina un producto de una sucursal específica."""
        if not all(isinstance(param, str) and param.strip() for param in [franquicia_id, sucursal_id, producto_id]):
            return self._response(HTTPStatus.BAD_REQUEST, "Parámetros inválidos: 'franquicia_id', 'sucursal_id' y 'producto_id' son obligatorios.")

        franquicia = self.repositorio.get_item({"FranquiciaID": franquicia_id})
        if not franquicia:
            return self._response(HTTPStatus.NOT_FOUND, "Franquicia no encontrada.")

        sucursal = next((s for s in franquicia.get("Sucursales", []) if s["SucursalID"] == sucursal_id), None)
        if not sucursal:
            return self._response(HTTPStatus.NOT_FOUND, "Sucursal no encontrada.")

        productos = sucursal.get("Productos", [])
        nuevos_productos = [p for p in productos if p["ProductoID"] != producto_id]

        if len(nuevos_productos) == len(productos):
            return self._response(HTTPStatus.NOT_FOUND, "Producto no encontrado.")

        sucursal["Productos"] = nuevos_productos

        if self.repositorio.actualizar_franquicia(franquicia_id, franquicia["Sucursales"]):
            return self._response(HTTPStatus.OK, "Producto eliminado exitosamente.")
        return self._response(HTTPStatus.INTERNAL_SERVER_ERROR, "Error al actualizar franquicia en DynamoDB.")

    def obtener_producto_mas_stock(self, franquicia_id: str) -> Dict[str, Any]:
        """Obtiene el producto con mayor stock dentro de una franquicia."""
        franquicia = self.repositorio.get_item({"FranquiciaID": franquicia_id})
        if not franquicia:
            return self._response(HTTPStatus.NOT_FOUND, "Franquicia no encontrada.")

        productos = [
            producto
            for sucursal in franquicia.get("Sucursales", [])
            for producto in sucursal.get("Productos", [])
        ]

        if not productos:
            return self._response(HTTPStatus.NOT_FOUND, "No se encontraron productos en la franquicia.")

        producto_mas_stock = max(productos, key=lambda p: p["Stock"])

        return self._response(HTTPStatus.OK, "Producto con mayor stock encontrado.", producto_mas_stock)

    @staticmethod
    def _response(status_code: int, message: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Genera una respuesta estándar en formato JSON."""
        response_body = {"message": message}
        if data:
            response_body["data"] = data
        return {"statusCode": status_code, "body": json.dumps(response_body)}
