import uuid
from typing import Optional, Dict, Any

class FranquiciaService:
    """Servicio para manejar operaciones CRUD de franquicias."""

    def __init__(self, repository):
        """Inicializa el servicio con un repositorio externo."""
        self.repository = repository

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
        
        self.repository.put_item(nueva_franquicia)
        return {
            "status": "success",
            "message": "Franquicia creada correctamente.",
            "data": nueva_franquicia
        }

    def obtener_franquicia(self, franquicia_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una franquicia por su ID."""
        return self.repository.get_item({"FranquiciaID": franquicia_id})

    def actualizar_franquicia(self, franquicia_id: str, nuevo_nombre: str) -> Dict[str, Any]:
        """Actualiza el nombre de una franquicia."""
        self._validar_nombre(nuevo_nombre)

        if not self.franquicia_existe(franquicia_id):
            return {"status": "error", "message": "Franquicia no encontrada."}

        self.repository.update_item(
            {"FranquiciaID": franquicia_id},
            "SET Nombre = :nombre",
            {":nombre": nuevo_nombre}
        )
        return {"status": "success", "message": "Franquicia actualizada."}

    def eliminar_franquicia(self, franquicia_id: str) -> Dict[str, Any]:
        """Elimina una franquicia por su ID."""
        if not self.franquicia_existe(franquicia_id):
            return {"status": "error", "message": "Franquicia no encontrada."}

        self.repository.delete_item({"FranquiciaID": franquicia_id})
        return {"status": "success", "message": "Franquicia eliminada."}

    @staticmethod
    def _validar_nombre(nombre: str):
        if not nombre:
            raise ValueError("El parámetro 'nombre' es obligatorio.")
