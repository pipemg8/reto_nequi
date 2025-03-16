import json
from http import HTTPStatus
from services.producto_service import ProductoService
from repositories.dynamo_repository import DynamoRepository

# Inicialización del servicio con DynamoDB como repositorio
repositorio_producto = DynamoRepository("Franquicias")
producto_service = ProductoService(repositorio_producto)

def response_json(status, message):
    """Genera una respuesta JSON estándar con encabezados."""
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(message)
    }

def manejar_productos(event, context):
    """
    Maneja las operaciones CRUD de productos dentro de sucursales.

    Parámetros:
    - event: Dict con la información de la solicitud HTTP.
    - context: Contexto de AWS Lambda.

    Retorna:
    - Dict con el código de estado y el cuerpo de la respuesta.
    """
    metodo = event.get("httpMethod", "").upper()
    ruta = event.get("path", "")

    # En POST, PUT y DELETE, los datos están en el body
    if metodo in ["POST", "PUT", "DELETE"]:
        try:
            params = json.loads(event.get("body", "{}"))
        except json.JSONDecodeError:
            return response_json(HTTPStatus.BAD_REQUEST, {"error": "El cuerpo de la solicitud no es un JSON válido"})
    else:
        params = event.get("queryStringParameters") or {}

    # 🔹 Manejo de ruta específica: "/productos/mas_stock"
    if metodo == "GET" and ruta == "/productos/mas_stock":
        return validar_y_ejecutar(
            producto_service.obtener_producto_mas_stock, 
            params, 
            ["franquicia_id"]
        )

    # 🔹 Manejo de operaciones CRUD estándar
    handlers = {
        "GET": lambda: validar_y_ejecutar(producto_service.obtener_producto, params, ["franquicia_id", "sucursal_id", "producto_id"]),
        "POST": lambda: validar_y_ejecutar(producto_service.agregar_producto, params, ["franquicia_id", "sucursal_id", "nombre"]),
        "PUT": lambda: validar_y_ejecutar(producto_service.actualizar_producto, params, ["franquicia_id", "sucursal_id", "producto_id", "stock"]),
        "DELETE": lambda: validar_y_ejecutar(producto_service.eliminar_producto, params, ["franquicia_id", "sucursal_id", "producto_id"])
    }

    return handlers.get(metodo, metodo_no_soportado)()

def validar_y_ejecutar(func, params, required_params):
    """Valida parámetros requeridos y ejecuta la función con manejo de errores."""
    faltantes = [param for param in required_params if param not in params or not params[param]]
    if faltantes:
        return response_json(HTTPStatus.BAD_REQUEST, {"error": f"Faltan parámetros: {', '.join(faltantes)}"})

    # Pasar todos los parámetros disponibles
    argumentos = {k: params[k] for k in required_params}
    if "nombre" in params:
        argumentos["nombre"] = params["nombre"]
    if "stock" in params:
        argumentos["stock"] = params["stock"]

    try:
        resultado = func(**argumentos)
        return response_json(HTTPStatus.OK, {"mensaje": "Operación exitosa", "resultado": resultado})
    except AttributeError as e:
        return response_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Error de atributo en el servicio", "detalle": str(e)})
    except Exception as e:
        return response_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Error interno en el servidor", "detalle": str(e)})

def metodo_no_soportado():
    """Respuesta estándar para métodos HTTP no soportados."""
    return response_json(HTTPStatus.METHOD_NOT_ALLOWED, {"error": "Método no permitido"})
