# NOTA:
# 1. **Commits**:
#    - Al realizar un commit, asegúrate de que el mensaje sea lo más específico posible.
#    - El mensaje de commit debe describir claramente qué cambios se realizaron en el código, por ejemplo:
#      "Añadir endpoint para consulta de usuario" o "Corregir error en la validación de contraseñas".
#      Evita mensajes vagos como "Arreglos generales" o "Cambio de código".
#    - Si el commit está relacionado con un bug, agrega el número del ticket o descripción del problema en el mensaje.
# 2. **Pull Requests**:
#    - Después de hacer tus cambios, realiza un *pull request* al repositorio principal (original).
#    - El pull request debe ser validado por un miembro del equipo antes de que se pueda fusionar.
#    - Asegúrate de que el pull request esté bien descrito, explicando qué cambios se realizaron y cualquier otra información relevante.
# 3. **Comentarios en el Código**:
#    - Es muy importante agregar comentarios explicativos en el código.
#    - Los comentarios deben ser claros y explicar la **lógica de negocio** o el **porqué** de ciertos bloques de código, no solo el **qué**.
#    - Ejemplo de buen comentario: "# Validamos que la contraseña tenga al menos 8 caracteres, una mayúscula y un número".
#    - Evitar comentarios innecesarios como "# Sumar dos números", si el código es obvio.


# Importamos Flask para crear la aplicación web
from flask import Flask

# Importamos CORS para permitir solicitudes desde otros orígenes (útil si el frontend está en otro dominio o puerto)
from flask_cors import CORS

# Importamos los Blueprints desde sus respectivos módulos de rutas
from routes.auth_routes import auth_bp        # Rutas relacionadas con autenticación
from routes.user_routes import user_bp        # Rutas relacionadas con usuarios
from routes.cotizar_routes import cotizar_bp  # Rutas para cotización de envíos
from routes.envios_routes import envios_bp    # Rutas para el manejo de envíos

# Creamos la instancia principal de la aplicación Flask
app = Flask(__name__)

# Habilitamos CORS en toda la aplicación (permite que el frontend acceda a esta API sin restricciones de origen)
CORS(app)

# Registramos los Blueprints para dividir y organizar nuestras rutas
app.register_blueprint(auth_bp)       # /auth, etc.
app.register_blueprint(user_bp)       # /user, etc.
app.register_blueprint(cotizar_bp)    # /cotizar, etc.
app.register_blueprint(envios_bp)     # /envios, etc.

# Iniciamos el servidor solo si ejecutamos este archivo directamente
if __name__ == "__main__":
    # Ejecutamos la app en el host 0.0.0.0 (accesible desde cualquier IP) y puerto 5000
    # El modo debug=True ayuda a ver errores y reinicia el servidor automáticamente al cambiar el código
    app.run(host="0.0.0.0", port=5001, debug=True)

