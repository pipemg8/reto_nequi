import uuid
from typing import Optional, Dict, Any
from repositories.dynamo_repository import DynamoRepository
from botocore.exceptions import BotoCoreError, ClientError


class FranquiciaService:
    """Servicio para manejar operaciones CRUD de franquicias con DynamoDB."""

    def __init__(self):
        self.repository = DynamoRepository("Franquicias")

    def franquicia_existe(self, franquicia_id: str) -> bool:
        """Verifica si una franquicia con el ID dado existe en la base de datos."""
        return self.repository.get_item({"FranquiciaID": franquicia_id}) is not None

    def crear_franquicia(self, nombre: str) -> Dict[str, Any]:
        """Crea una nueva franquicia en la base de datos."""
        self._validar_nombre(nombre)

        nueva_franquicia = {
            "FranquiciaID": str(uuid.uuid4()),
            "Nombre": nombre,
            "Sucursales": []
        }

        try:
            self.repository.put_item(nueva_franquicia)
            return nueva_franquicia
        except (ClientError, BotoCoreError) as e:
            raise RuntimeError(f"Error en DynamoDB: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error desconocido: {str(e)}")

    def obtener_franquicia(self, franquicia_id: str) -> Dict[str, Any]:
        """Obtiene una franquicia por ID."""
        self._validar_id(franquicia_id)

        franquicia = self.repository.get_item({"FranquiciaID": franquicia_id})
        if not franquicia:
            raise KeyError("Franquicia no encontrada.")

        return franquicia

    def actualizar_franquicia(self, franquicia_id: str, nuevo_nombre: str) -> Dict[str, Any]:
        """Actualiza el nombre de una franquicia existente."""
        self._validar_id(franquicia_id)
        self._validar_nombre(nuevo_nombre)

        franquicia = self.repository.get_item({"FranquiciaID": franquicia_id})
        if not franquicia:
            raise KeyError("La franquicia no existe.")

        try:
            self.repository.update_item(
                {"FranquiciaID": franquicia_id},
                "SET Nombre = :nombre",
                {":nombre": nuevo_nombre}
            )
            return {"FranquiciaID": franquicia_id, "Nombre": nuevo_nombre}
        except (ClientError, BotoCoreError) as e:
            raise RuntimeError(f"Error en DynamoDB: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error desconocido: {str(e)}")

    def eliminar_franquicia(self, franquicia_id: str) -> None:
        """Elimina una franquicia por su ID."""
        self._validar_id(franquicia_id)

        franquicia = self.repository.get_item({"FranquiciaID": franquicia_id})
        if not franquicia:
            raise KeyError("La franquicia no existe.")

        try:
            self.repository.delete_item({"FranquiciaID": franquicia_id})
        except (ClientError, BotoCoreError) as e:
            raise RuntimeError(f"Error en DynamoDB: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error desconocido: {str(e)}")

    @staticmethod
    def _validar_id(franquicia_id: str):
        if not franquicia_id:
            raise ValueError("El parámetro 'franquicia_id' es obligatorio.")

    @staticmethod
    def _validar_nombre(nombre: str):
        if not nombre:
            raise ValueError("El parámetro 'nombre' es obligatorio.")
