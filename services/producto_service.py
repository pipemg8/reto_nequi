"""
Módulo de servicio para la gestión de productos en sucursales.
"""

import uuid
import json
from services.sucursal_service import SucursalService
from typing import Dict, Any, Optional

class ProductoService:
    """Servicio para gestionar productos en sucursales."""

    def __init__(self):
        self.sucursal_service = SucursalService()

    def agregar_producto(self, franquicia_id: str, sucursal_id: str, nombre: str) -> Dict[str, Any]:
        """
        Agrega un producto a una sucursal de una franquicia.

        Retorna:
        - Respuesta estándar con código de estado y mensaje.
        """
        if not franquicia_id or not sucursal_id or not nombre:
            return self._response(400, "Se requieren 'franquicia_id', 'sucursal_id' y 'nombre'.")

        franquicia = self.sucursal_service.obtener_franquicia(franquicia_id)
        if not franquicia:
            return self._response(404, "Franquicia no encontrada.")

        sucursal = self.sucursal_service.obtener_sucursal(franquicia, sucursal_id)
        if not sucursal:
            return self._response(404, "Sucursal no encontrada.")

        producto_id = str(uuid.uuid4())
        sucursal.setdefault("Productos", []).append({
            "ProductoID": producto_id,
            "Nombre": nombre
        })

        try:
            self.sucursal_service.actualizar_franquicia(franquicia_id, franquicia["Sucursales"])
            return self._response(201, "Producto creado exitosamente.", {"ProductoID": producto_id})
        except Exception as e:
            return self._response(500, f"Error al agregar producto: {str(e)}")

    def eliminar_producto(self, sucursal_id: str, producto_id: str) -> Dict[str, Any]:
        """
        Elimina un producto de una sucursal.

        Retorna:
        - Respuesta estándar con código de estado y mensaje.
        """
        if not sucursal_id or not producto_id:
            return self._response(400, "Se requieren 'sucursal_id' y 'producto_id'.")

        # Obtener todas las franquicias para buscar la sucursal
        franquicias = self.sucursal_service.obtener_todas_franquicias()
        for franquicia in franquicias:
            sucursal = self.sucursal_service.obtener_sucursal(franquicia, sucursal_id)
            if sucursal:
                productos = sucursal.get("Productos", [])
                for producto in productos:
                    if producto["ProductoID"] == producto_id:
                        productos.remove(producto)
                        try:
                            self.sucursal_service.actualizar_franquicia(franquicia["FranquiciaID"], franquicia["Sucursales"])
                            return self._response(200, "Producto eliminado exitosamente.")
                        except Exception as e:
                            return self._response(500, f"Error al eliminar producto: {str(e)}")
                return self._response(404, "Producto no encontrado.")

        return self._response(404, "Sucursal no encontrada.")

    @staticmethod
    def _response(status_code: int, message: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Genera una respuesta estándar."""
        response_body = {"message": message}
        if data:
            response_body["data"] = data
        return {"statusCode": status_code, "body": json.dumps(response_body)}
