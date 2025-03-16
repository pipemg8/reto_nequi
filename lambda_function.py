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
    print(f"🔍 Evento recibido: {json.dumps(event, indent=2)}")
    print(f"➡️ Ruta recibida: {ruta}, Método recibido: {metodo}")

    # Métodos permitidos
    metodos_permitidos = {"GET", "POST", "PUT", "DELETE"}

    # 🚀 Nueva verificación: Si no se recibe un método válido
    if not metodo:
        print("❌ ERROR: No se recibió un método HTTP válido.")
        return {"statusCode": 400, "body": json.dumps({"error": "Método HTTP no especificado."})}

    # Validar método HTTP antes de procesar rutas
    if metodo not in metodos_permitidos:
        print(f"❌ ERROR: Método '{metodo}' no permitido.")
        return {"statusCode": 405, "body": json.dumps({"error": "Método no soportado."})}

    # ✅ Mantenimiento del manejo de rutas sin alteraciones
    if ruta == "/":
        return {"statusCode": 200, "body": json.dumps({"message": "API funcionando correctamente"})}
    
    elif ruta == "/sucursales":
        if metodo == "PUT":
            try:
                # Manejo seguro del body
                body = json.loads(event["body"]) if event.get("body") else {}

                # Extraer datos del body
                franquicia_id = body.get("franquicia_id")
                sucursal_id = body.get("sucursal_id")
                nuevo_nombre = body.get("nuevo_nombre")

                print(f"✏️ Datos recibidos - franquicia_id: {franquicia_id}, sucursal_id: {sucursal_id}, nuevo_nombre: {nuevo_nombre}")

                # Validaciones específicas
                if not franquicia_id:
                    print("❌ ERROR: 'franquicia_id' es requerido.")
                    return {"statusCode": 400, "body": json.dumps({"error": "Se requiere 'franquicia_id'"})}

                if not sucursal_id:
                    print("❌ ERROR: 'sucursal_id' es requerido.")
                    return {"statusCode": 400, "body": json.dumps({"error": "Se requiere 'sucursal_id'"})}

                if not nuevo_nombre:
                    print("❌ ERROR: 'nuevo_nombre' es requerido.")
                    return {"statusCode": 400, "body": json.dumps({"error": "Se requiere 'nuevo_nombre'"})}

                # Llamar a la capa de servicio
                response = manejar_sucursales(event, context)
                print(f"✅ Respuesta de manejar_sucursales: {response}")

                return response
            
            except json.JSONDecodeError:
                print("❌ ERROR: JSON inválido en la solicitud.")
                return {"statusCode": 400, "body": json.dumps({"error": "Formato JSON inválido."})}

        return manejar_sucursales(event, context)

    elif ruta == "/productos":
        return manejar_productos(event, context)
    
    elif ruta == "/productos/mas_stock":
        return manejar_productos(event, context)
    
    elif ruta == "/franquicias":
        respuesta = manejar_franquicias(event, context)
        print(f"✅ Respuesta de manejar_franquicias: {respuesta}")
        return respuesta

    # ❌ Si la ruta no se encuentra
    print(f"❌ ERROR: Ruta '{ruta}' no encontrada.")
    return {"statusCode": 404, "body": json.dumps({"error": "Ruta no encontrada"})}
