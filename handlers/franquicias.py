from services.franquicia_service import FranquiciaService

servicio = FranquiciaService()

def lambda_handler(event, context):
    """Manejador Lambda para operaciones sobre franquicias."""
    http_method = event.get("httpMethod", "")
    params = event.get("queryStringParameters", {}) or {}

    if http_method == "POST":
        return servicio.crear_franquicia(params.get("nombre"))

    if http_method == "PUT":
        return servicio.actualizar_franquicia(params.get("id"), params.get("nombre"))

    if http_method == "DELETE":
        return servicio.eliminar_franquicia(params.get("id"))

    return {"statusCode": 400, "body": "Método no soportado."}
