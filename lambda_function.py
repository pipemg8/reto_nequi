import json
from handlers.franquicias import manejar_franquicias
from handlers.sucursales import manejar_sucursales
from handlers.productos import manejar_productos

def lambda_handler(event, context):
    """Manejador principal de la API Lambda"""

    # Extraer valores con manejo de errores
    ruta = event.get("resource", "/").strip()
    metodo = event.get("httpMethod", "").strip().upper()

    # Logs para depuración sin emojis para evitar errores de codificación
    print(f"Evento recibido: {json.dumps(event, indent=2)}")
    print(f"Ruta recibida: {ruta}, Método recibido: {metodo}")

    # Métodos permitidos
    metodos_permitidos = {"GET", "POST", "PUT", "DELETE"}

    if not metodo:
        print("ERROR: No se recibió un método HTTP válido.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Método HTTP no especificado."}),
        }

    if metodo not in metodos_permitidos:
        print(f"ERROR: Método '{metodo}' no permitido.")
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Método no soportado."}),
        }

    # ✅ Ruta principal de salud
    if ruta == "/":
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "API funcionando correctamente"}),
        }

    # Manejo de sucursales
    elif ruta == "/sucursales":
        if metodo == "PUT":
            try:
                print(f"Ejecutando manejar_sucursales... {manejar_sucursales}")  # Verificar importación
                
                raw_body = event.get("body", "{}")
                body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body

                franquicia_id = body.get("franquicia_id")
                sucursal_id = body.get("sucursal_id")
                nuevo_nombre = body.get("nuevo_nombre")

                errores = {}
                if not franquicia_id:
                    errores["franquicia_id"] = "Se requiere 'franquicia_id'"
                if not sucursal_id:
                    errores["sucursal_id"] = "Se requiere 'sucursal_id'"
                if not nuevo_nombre:
                    errores["nuevo_nombre"] = "Se requiere 'nuevo_nombre'"

                if errores:
                    print(f"Errores detectados: {errores}")
                    return {
                        "statusCode": 400,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps({"error": errores}),
                    }

                # Llamada a manejar_sucursales con try-except para capturar errores
                try:
                    respuesta = manejar_sucursales(event, context)
                    print(f"Respuesta de manejar_sucursales: {respuesta}")
                    return respuesta
                except Exception as e:
                    print(f"ERROR al ejecutar manejar_sucursales: {str(e)}")
                    return {
                        "statusCode": 500,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps({"error": "Error interno en manejar_sucursales."}),
                    }
                    
            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Formato JSON inválido."}),
                }

        return manejar_sucursales(event, context)
        
        # Si es otro método, seguir con el flujo normal
        return manejar_sucursales(event, context)

    # ✅ Manejo de productos
    elif ruta in ["/productos", "/productos/mas_stock"]:
        return manejar_productos(event, context)

    # ✅ Manejo de franquicias
    elif ruta == "/franquicias":
        respuesta = manejar_franquicias(event, context)
        print(f"Respuesta de manejar_franquicias: {respuesta}")
        return respuesta

    # ❌ Si la ruta no se encuentra
    print(f"ERROR: Ruta '{ruta}' no encontrada.")
    return {
        "statusCode": 404,
        "body": json.dumps({"error": "Ruta no encontrada"}),
    }
