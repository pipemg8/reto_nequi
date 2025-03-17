# Reto Nequi - Documentación de despliegue

--Este documento describe los pasos para desplegar 

## 1. Requisitos previos
Antes de comenzar, asegúrese de tener instalados los siguientes componentes:

- **AWS CLI**: [Instalar AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- **Docker**: [Instalar Docker](https://docs.docker.com/get-docker/)
- **Python 3.x** y **pip**: [Instalar Python](https://www.python.org/downloads/)
- **Visual Studio Code** (opcional, recomendado): [Descargar VS Code](https://code.visualstudio.com/)
- **Postman** (para probar los servicios): [Descargar Postman](https://www.postman.com/downloads/)
- **Cuenta de AWS** con permisos suficientes para desplegar recursos.
- **Git**: [Instalar Git](https://git-scm.com/downloads)

---

## 2. Clonar el repositorio

Ejecuta el siguiente comando en la terminal para clonar el repositorio:

```bash
git clone https://github.com/pipemg8/reto_nequi.git
cd reto_nequi
```

---

## 3. Configurar credenciales de AWS

Para que los despliegues funcionen, debes configurar tus credenciales de AWS en tu entorno local. Ejecuta:

```bash
aws configure
```

Ingresa la siguiente información cuando se te solicite:
- AWS Access Key ID
- AWS Secret Access Key
- Region: `us-east-1` (o la que corresponda)
- Output format: `json`

Si ya tienes configuradas las credenciales, puedes verificarlas ejecutando:
```bash
aws sts get-caller-identity
```

---

## 4. Ejecutar la aplicación localmente

Para ejecutar la aplicación en local:

1. **Crear un entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Mac/Linux
   venv\Scripts\activate     # En Windows
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación localmente con SAM CLI:**
   ```bash
   sam local start-api
   ```
   Esto iniciará un servidor local simulando AWS API Gateway.

4. **Probar los endpoints en Postman:**
   - Endpoint local: `http://127.0.0.1:3000/franquicias?franquicia_id=123`
   - Para probar diferentes operaciones, usa los métodos GET, POST, PUT y DELETE según corresponda.

---

## 5. Desplegar la infraestructura a AWS

La infraestructura como código está definida en el archivo `retonequi2025.yaml` y se despliega usando AWS CloudFormation.

1. **Validar la plantilla antes del despliegue:**
   ```bash
   aws cloudformation validate-template --template-body file://retonequi2025.yaml
   ```

2. **Crear o actualizar la infraestructura en AWS:**
   ```bash
   aws cloudformation deploy \
     --template-file retonequi2025.yaml \
     --stack-name RetoNequiStack \
     --capabilities CAPABILITY_NAMED_IAM
   ```

3. **Verificar el estado del stack:**
   ```bash
   aws cloudformation describe-stacks --stack-name RetoNequiStack
   ```

---

## 6. Configuración de CI/CD con GitHub Actions

El flujo de despliegue automático está definido en `.github/workflows/deploy-lambda.yml` y permite desplegar cambios automáticamente a AWS cada vez que se realiza un push a la rama principal.

1. **Verificar el archivo de configuración en GitHub Actions:**
   - Ubicación: `.github/workflows/deploy-lambda.yml`
   - Asegúrate de que las credenciales de AWS están configuradas en GitHub como `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY`.

2. **Hacer un commit y push para activar el pipeline:**
   ```bash
   git add .
   git commit -m "Actualización de código"
   git push origin main
   ```

3. **Monitorear la ejecución en GitHub Actions:**
   - Ve a la pestaña `Actions` en tu repositorio de GitHub.
   - Busca el workflow `deploy-lambda.yml` y revisa su estado.

---

## 7. Probar los servicios en AWS

Una vez desplegada la aplicación, los servicios están disponibles en AWS API Gateway. Puedes probarlos en Postman con los siguientes endpoints:

### **GET - Consultar franquicia**
```bash
GET https://y2xotln9b8.execute-api.us-east-1.amazonaws.com/productivo/franquicias?franquicia_id=123
```

### **POST - Crear franquicia**
```bash
POST https://y2xotln9b8.execute-api.us-east-1.amazonaws.com/productivo/franquicias
Content-Type: application/json

{
    "nombre": "Franquicia pereira"
}
```

### **POST - Crear sucursal**
```bash
POST https://y2xotln9b8.execute-api.us-east-1.amazonaws.com/productivo/sucursales?franquicia_id=0e1dbfbe-371a-459d-9a83-ed7ad0ae2fa9
Content-Type: application/json

{
  "nombre": "Sucursal rio sur"
}
```

### **POST - Agregar producto a sucursal**
```bash
POST https://y2xotln9b8.execute-api.us-east-1.amazonaws.com/productivo/productos
Content-Type: application/json

{
  "franquicia_id": "123",
  "sucursal_id": "783c6c08-ec3d-4103-9b15-af31d31fcb65",
  "nombre": "Producto Z"
}
```

### **DELETE - Eliminar producto de sucursal**
```bash
DELETE https://y2xotln9b8.execute-api.us-east-1.amazonaws.com/productivo/productos
Content-Type: application/json

{
    "franquicia_id":"123",
    "sucursal_id":"783c6c08-ec3d-4103-9b15-af31d31fcb65",
    "producto_id":"aa4a65e9-443e-48ad-bb9b-909d111c4b94"
}
```

### **PUT - Modificar nombre y stock producto**
```bash
PUT https://y2xotln9b8.execute-api.us-east-1.amazonaws.com/productivo/productos
Content-Type: application/json

{
  "franquicia_id": "123",
  "sucursal_id": "783c6c08-ec3d-4103-9b15-af31d31fcb65",
  "producto_id": "b519c1bd-70df-41af-b493-74cceafbbad1",
  "nombre": "Producto Z",
  "stock": 330
}
```

---
Siguiendo estos pasos, puedes desplegar y ejecutar la aplicación tanto en un entorno local como en AWS.
