"""
Módulo de servicio para la gestión de productos en sucursales.
"""

import uuid
from services.sucursal_service import SucursalService

class ProductoService:
    """Servicio para gestionar productos en sucursales."""

    def __init__(self):
        self.sucursal_service = SucursalService()

    def agregar_producto(self, franquicia_id: str, sucursal_id: str, nombre: str):
        """
        Agrega un producto a una sucursal de una franquicia.

        Parámetros:
        - franquicia_id: ID de la franquicia.
        - sucursal_id: ID de la sucursal.
        - nombre: Nombre del producto.

        Retorna:
        - Diccionario con mensaje de éxito y el ID del producto.
        """
        franquicia = self.sucursal_service.obtener_franquicia(franquicia_id)
        if not franquicia:
            return {"error": "Franquicia no encontrada"}, 404

        sucursal = self.sucursal_service.obtener_sucursal(franquicia, sucursal_id)
        if not sucursal:
            return {"error": "Sucursal no encontrada"}, 404

        producto_id = str(uuid.uuid4())
        sucursal.setdefault("Productos", []).append({
            "ProductoID": producto_id,
            "Nombre": nombre
        })

        self.sucursal_service.actualizar_franquicia(franquicia_id, franquicia["Sucursales"])

        return {"message": "Producto creado", "ProductoID": producto_id}, 201
