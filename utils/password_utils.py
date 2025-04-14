import bcrypt

# Función para encriptar la contraseña del usuario al registrarse
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Función para verificar la contraseña encriptada al iniciar sesión
def verificar_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))