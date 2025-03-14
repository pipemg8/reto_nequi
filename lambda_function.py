import json
from handlers.franquicias import manejar_franquicias
from handlers.sucursales import manejar_sucursales
from handlers.productos import manejar_productos

def lambda_handler(event, context):
    ruta = event.get("path", "")
    metodo = event.get("httpMethod", "")

    print(f"Ruta recibida: {ruta}, Método recibido: {metodo}")  # Para depuración

    # Lista de métodos permitidos
    metodos_permitidos = ["GET", "POST", "PUT", "DELETE"]
    
    if metodo not in metodos_permitidos:
        return {"statusCode": 400, "body": json.dumps({"error": "Método no soportado."})}

    if ruta == "/":
        return {"statusCode": 200, "body": json.dumps({"message": "API funcionando correctamente"})}
    elif ruta.startswith("/sucursales"):
        return manejar_sucursales(event, metodo)
    elif ruta.startswith("/productos"):
        return manejar_productos(event, metodo)
    elif ruta.startswith("/franquicias"):
        return manejar_franquicias(event, metodo)

    return {"statusCode": 404, "body": json.dumps({"error": "Ruta no encontrada"})}
