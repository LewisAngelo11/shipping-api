# API de Gestión de Usuarios y Cotización

Este es un proyecto basado en Flask que interactúa con una base de datos MySQL para gestionar usuarios y cotizar servicios de paquetería. La API permite realizar operaciones como login, creación y consulta de usuarios, así como la cotización de paquetes y envíos.

## Requisitos

- Python 3.8 o superior
- Flask
- MySQL
- mysql-connector-python

## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/LewisAngelo11/shipping-api
    cd shipping-api
    ```

2. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

3. Configura la conexión a tu base de datos MySQL. Asegúrate de tener un archivo `.env` o modificar las credenciales en el código.

4. Inicia el servidor de desarrollo:
    ```bash
    flask run
    ```

## Configuración de la Base de Datos

En tu archivo `app.py`, la función `obtener_conexion()` gestiona la conexión con la base de datos MySQL. Asegúrate de configurar correctamente los parámetros de conexión como el host, el usuario y la contraseña.

```python
def obtener_conexion():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="tu_usuario",
            password="tu_contraseña",
            database="bd",
            auth_plugin="mysql_native_password"
        )
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None
```

## Endpoints

### 1. **Login**

- **Método:** `POST`
- **Ruta:** `/login`
- **Descripción:** Permite validar el acceso de un usuario a la página.
- **Parámetros de entrada:**
  - `Usuario`: Nombre del usuario.
  - `Contrasena`: Contraseña del usuario.


- **Respuesta exitosa (200):**
```json
{
  "status": "success",
  "rol": "Usuario"
}
  ```
- **Respuesta de error (401):**
```json
{
  "status": "error",
  "mensaje": "Credenciales incorrectas"
}
  ```

### 2. **Crear Usuario**

- **Método:** `POST`
- **Ruta:** `/api/usuario`
- **Descripción:** Crea un nuevo usuario en la base de datos.
- **Parámetros de entrada:**
    - `Nombre`: Nombre del usuario.
    - `Apellido1`: Primer apellido.
    - `Apellido2`: Segundo apellido.
    - `Fecha_Nacimiento`: Fecha de nacimiento.
    - `Email`: Correo electrónico.
    - `Usuario`: Nombre de usuario.
    - `Contrasena`: Contraseña del usuario.


- **Respuesta exitosa (201):**
```json
{
  "status": "success",
  "mensaje": "Usuario creado"
}
  ```

- **Respuesta de error (401):**
```json
{
  "status": "error",
  "mensaje": "Error al crear el usuario"
}
   ```

### 3. **Consultar Usuario**

- **Método:** `GET`
- **Ruta:** `/usuario/consultar`
- **Descripción:** Consulta la información de un usuario por su nombre de usuario.
- **Parámetros de entrada:**
    - `username`: Nombre de usuario a consultar.


- **Respuesta exitosa (200):**
```json
{
  "status": "success",
  "username": "nombre_usuario",
  "Apellido1": "apellido1",
  "Apellido2": "apellido2",
  "Fecha_Nacimiento": "fecha_nac",
  "Edad": "edad",
  "Email": "email",
  "User": "usuario",
  "Contraseña": "contrasena"
}
   ```

- **Respuesta de error (404):**
```json
{
  "status": "error",
  "mensaje": "Usuario no encontrado"
}
```

### 4. **Actualizar Usuario**

- **Método:** `PUT`
- **Ruta:** `/api/usuarios/<int:id>`
- **Descripción:** Actualiza la información de un usuario existente en la base de datos.
- **Parámetros de entrada:**
    - `id`: ID del usuario a actualizar.
    - `usuario`: Nuevo nombre de usuario.
    - `contrasena`: Nueva contraseña.
    - `Rol`: Nuevo rol del usuario (opcional).}


- **Respuesta exitosa (200):**
```json
{
  "status": "success",
  "mensaje": "Usuario actualizado"
}
```

- **Respuesta de error (400):**
```json
{
  "status": "error",
  "mensaje": "Error al actualizar el usuario"
}
```

### 5. **Eliminar Usuario**

- **Método:** `DELETE`
- **Ruta:** `/eliminarUsers`
- **Descripción:** Elimina un usuario de la base de datos.
- **Parámetros de entrada:**
    - `contraseña`: Contraseña del usuario a eliminar.


- **Respuesta exitosa (200):**
```json
{
  "status": "success"
}
```

- **Respuesta de error (400):**
```json
{
  "status": "error",
  "mensaje": "Error al eliminar el usuario"
}
```

### 6. **Cotizar CP**

- **Método:** `POST`
- **Ruta:** `/Cotizar/CP`
- **Descripción:** Es el primer paso para cotizar un envio buscando los datos de ubicación con el CP.
- **Parámetros de entrada:**
    - `CP`: Código postal para devolver los datos como estado, municipio y ciudad.


- **Respuesta exitosa (200):**
```json
{
  "status": "success"
}
```

- **Respuesta de error (400):**
```json
{
  "status": "error",
  "mensaje": "No se encontraron datos"
}
```


### 7. **Cotizar Paquete**
- **Método:** `POST`
- **Ruta:** `/Cotizar/Paquete`
- **Descripción:** Es el segundo paso para cotizar un envio ingresando las dimensiones del paquete.
- **Parámetros de entrada:**
    - `Alto`: El alto del paquete.
    - `Ancho`: El acho del paquete.
    - `Peso`: El peso del paquete.


- **Respuesta exitosa (200):**
```json
{
  "status": "success, tarifa, pesovm, distancia"
}
```


- **Respuesta de error (400):**
```json
{
  "status": "error",
  "mensaje": "No se pudo cotizar el paquete."
}
```


### 8. **Envios**
- **Método:** `POST`
- **Ruta:** `/Cotizar/Envio`
- **Descripción:** Es el tercer paso para cotizar un envio asignando ya un remitente y destinatario.
- **Parámetros de entrada:**
    - `Remitente`: El remitente del envio.
    -  `Destinatario`: El destinatario del envio


- **Respuesta exitosa (200):**
```json
{
  "status": "success",
  "mensaje": "Datos procesados correctamente, Numero de rastreo: "
}
```

- **Respuesta de error (400):**
```json
{
  "status": "error",
  "mensaje": "No se pudo concretar el envio."
}
```

### 9. **Rastrear Envios**
- **Método:** `GET`
- **Ruta:** `/rastrear/rastreo`
- **Descripción:** Este metodo es para el rastreo de envios con el número de rastreo.
- **Parámetros de entrada:**
    - `Numero de rastreo`: El número de rastreo asociado al paquete y al envío.


- **Respuesta exitosa (200):**
```json
{
  "status": "success",
  "mensaje": "id_Envio: resultado[0], id_Paquete: resultado[1], Estatus: resultado[2], Remitente: resultado[3], Destinatario: resultado[4],"
}
```

- **Respuesta de error (400):**
```json
{
  "status": "error",
  "mensaje": "Numero de rastreo no encontrado."
}
```


## Tecnologías Utilizadas:
-  **Python 3.x**
-  **Flask**
-  **MySQL**
-  **Geopy (para cálculo de distancias)**
-  **JSON para entrada y salida de datos**