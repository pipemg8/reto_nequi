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

    if not metodo:
        print("❌ ERROR: No se recibió un método HTTP válido.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Método HTTP no especificado."}),
        }

    if metodo not in metodos_permitidos:
        print(f"❌ ERROR: Método '{metodo}' no permitido.")
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Método no soportado."}),
        }

    if ruta == "/":
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "API funcionando correctamente"}),
        }

    elif ruta == "/sucursales":
        if metodo == "PUT":
            try:
                # 🔹 Asegurar que event["body"] siempre sea un diccionario JSON válido
                raw_body = event.get("body", "{}")
                print(f"📌 Tipo de event['body']: {type(raw_body)}")
                print(f"📥 Contenido bruto de event['body']: {raw_body}")

                if isinstance(raw_body, str):
                    body = json.loads(raw_body)
                else:
                    body = raw_body  # En caso de que ya sea un dict

                print(f"📌 Cuerpo después de parseo: {body}")

                franquicia_id = body.get("franquicia_id")
                sucursal_id = body.get("sucursal_id")
                nuevo_nombre = body.get("nuevo_nombre")

                if not franquicia_id:
                    return {
                        "statusCode": 400,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps({"error": "Se requiere 'franquicia_id'"}),
                    }
                if not sucursal_id:
                    return {
                        "statusCode": 400,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps({"error": "Se requiere 'sucursal_id'"}),
                    }
                if not nuevo_nombre:
                    return {
                        "statusCode": 400,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps({"error": "Se requiere 'nuevo_nombre'"}),
                    }

                response = manejar_sucursales(event, context)
                return response

            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Formato JSON inválido."}),
                }

        return manejar_sucursales(event, context)

    elif ruta == "/productos":
        return manejar_productos(event, context)

    elif ruta == "/productos/mas_stock":
        return manejar_productos(event, context)

    elif ruta == "/franquicias":
        respuesta = manejar_franquicias(event, context)
        print(f"✅ Respuesta de manejar_franquicias: {respuesta}")
        return respuesta

    print(f"❌ ERROR: Ruta '{ruta}' no encontrada.")
    return {
        "statusCode": 404,
        "body": json.dumps({"error": "Ruta no encontrada"}),
    }
