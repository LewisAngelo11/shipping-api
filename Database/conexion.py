import mysql.connector
from config import DB_CONFIG

# Funcion para obtener la conexion a la base de datos
def obtener_conexion():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None