import services.franquicia_service

franquicia_service = services.franquicia_service.FranquiciaService()

def lambda_handler(event, context):
    """Manejador Lambda para operaciones sobre franquicias."""
    http_method = event.get("httpMethod", "")
    params = event.get("queryStringParameters", {}) or {}

    if http_method == "POST":
        return franquicia_service.crear_franquicia(params.get("nombre"))

    if http_method == "PUT":
        return franquicia_service.actualizar_franquicia(params.get("id"), params.get("nombre"))

    if http_method == "DELETE":
        return franquicia_service.eliminar_franquicia(params.get("id"))

    return {"statusCode": 400, "body": "Método no soportado."}
