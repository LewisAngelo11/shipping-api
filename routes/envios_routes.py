# Endpoints para los metodos de envios como el de realizar envios como el de rastrar envios

from flask import Blueprint, request, jsonify
from Database.conexion import obtener_conexion
import random

envios_bp = Blueprint ('envios', __name__)

# Función para realizar envios.
@envios_bp.route('/Cotizar/Envio', methods=['POST'])
def Envios():
    datos = request.json
    required_keys = ['Origen', 'Destino', 'Peso', 'Largo', 'Alto', 'Ancho', 'EmailR', 'EmailD']

    # Verificar si los atributos existen en los datos
    if not all(key in datos for key in required_keys):
        return jsonify({"status": "error", "mensaje": "Datos incompletos"}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(buffered=True)

    try:
        # Insertar en Paquete
        cursor.execute("INSERT INTO Paquete (Peso, Estatus, Largo, Alto, Ancho) VALUES (%s, %s, %s, %s, %s);",
                       (datos['Peso'], 'EN PROCESO', datos['Largo'], datos['Alto'], datos['Ancho']))
        conexion.commit()

        # Obtener Id del remitente
        cursor.execute("SELECT id_Usuario FROM paqueteria.usuario WHERE Email = %s;", (datos['EmailR'],))
        Id_Remitente = cursor.fetchone()
        if not Id_Remitente:
            raise ValueError("Remitente no encontrado")
        Id_Remitente = Id_Remitente[0]

        # Obtener Id del destinatario
        cursor.execute("SELECT id_Usuario FROM paqueteria.usuario WHERE Email = %s;", (datos['EmailD'],))
        Id_Destinatario = cursor.fetchone()
        if not Id_Destinatario:
            raise ValueError("Destinatario no encontrado")
        Id_Destinatario = Id_Destinatario[0]

        # Obtener Id del paquete
        cursor.execute(
            "SELECT max(id_Paquete) FROM paqueteria.paquete WHERE Peso = %s and Largo = %s and Alto = %s and Ancho = %s;",
            (datos['Peso'], datos['Largo'], datos['Alto'], datos['Ancho']))
        Id_Paquete = cursor.fetchone()[0]

        # Insertar en Envio
        cursor.execute(
            "INSERT INTO envio(Fecha_Entrega, Costo, Origen, Destino, id_Paquete, id_Remitente, id_Destinatario, Estatus) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
            (datos['FechaR'], float(datos['tarifa'].replace('$', '')), datos['Origen'], datos['Destino'], Id_Paquete,
             Id_Remitente, Id_Destinatario, 'EN PROCESO'))
        conexion.commit()

        # Crear código de rastreo
        rastreo_code = ''.join([str(random.randint(0, 9)) for _ in range(20)])

        # Insertar en Rastreo
        cursor.execute(
            "SELECT max(id_Envio) FROM paqueteria.envio WHERE Fecha_Entrega = %s and Costo = %s and Origen = %s and Destino = %s and id_Paquete = %s and id_Remitente = %s and id_Destinatario = %s;",
            (datos['FechaR'], float(datos['tarifa'].replace('$', '')), datos['Origen'], datos['Destino'], Id_Paquete,
             Id_Remitente, Id_Destinatario))
        Id_Envio = cursor.fetchone()[0]
        cursor.execute("INSERT INTO rastreo(Codigo_Rastreo, id_Paquete, id_Envio) VALUES (%s, %s, %s);",
                       (rastreo_code, Id_Paquete, Id_Envio))
        conexion.commit()

    except Exception as err:
        print(err)
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        cursor.close()
        conexion.close()

    return jsonify({"status": "success", "mensaje": "Datos procesados correctamente", "Rastreo_Code": rastreo_code}), 200

# CORRECIONES: En esta función probar con el metodo "GET" en vez de "POST"
# Función para rastrear un envio con el código de rastreo
@envios_bp.route("/rastrear/rastreo", methods=["POST"])
def rastrear_envio():
    conexion = obtener_conexion()
    datos = request.json  # Obtiene los datos del archivo json de la página web
    rastreo = datos.get("Rastreo")
    print("Número de rastreo:", rastreo)  # Imprime solo el número de rastreo para depuración

    if not conexion:
        return jsonify({"status": "error", "mensaje": "Error de conexión con la base de datos"}), 500

    cursor = conexion.cursor()

    # Asegúrate de pasar el rastreo como una tupla y modificar la consulta SQL
    cursor.execute("""
        SELECT 
            e.id_Envio, 
            r.id_Paquete, 
            e.Estatus, 
            CONCAT(ur.Nombre, ' ', ur.Apellido1, ' ', ur.Apellido2) AS Remitente,
            CONCAT(ud.Nombre, ' ', ud.Apellido1, ' ', ud.Apellido2) AS Destinatario
        FROM 
            rastreo r
        JOIN 
            envio e ON r.id_Envio = e.id_Envio
        JOIN 
            usuario ur ON e.id_Remitente = ur.id_Usuario
        JOIN 
            usuario ud ON e.id_Destinatario = ud.id_Usuario
        WHERE 
            r.Codigo_Rastreo = %s
    """, (rastreo,))

    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()

    if resultado:
        # Si el resultado se encuentra, devuelve los datos de manera estructurada
        return jsonify({
            "status": "success",
            "id_Envio": resultado[0],
            "id_Paquete": resultado[1],
            "Estatus": resultado[2],
            "Remitente": resultado[3],
            "Destinatario": resultado[4],

        }), 200
    return jsonify({"status": "error", "mensaje": "Numero de rastreo no encontrado"}), 404