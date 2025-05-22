# Endpoints para los metodos de envios como el de realizar envios como el de rastrar envios

from flask import Blueprint, request, jsonify
from sqlalchemy.testing.pickleable import EmailUser

from app.config.config_sqlalchemy import get_session
from sqlalchemy import func
from sqlalchemy.orm import aliased
import random

from app.models.envio import Envio, EstatusEnvio
from app.models.rastreo import Rastreo
from app.models.paquete import Paquete
from app.models.usuario import Usuario

envios_bp = Blueprint ('envios', __name__)

# Obtener el id del usuario por el correo
def obtener_id_usuario(email_usuario, session):
    usuario = session.query(Usuario).filter_by(Email=email_usuario).first()
    if not usuario:
        raise ValueError("Usuario no encontrado")
    return usuario.id_Usuario


# Función para realizar envios.
@envios_bp.route('/Cotizar/Envio', methods=['POST'])
def Envios():
    datos = request.json
    paquetes_data = datos.get('paquetes', [])
    paquetes_creados = []

    db = get_session()

    # Obtener Id del remitente
    email_remitente = datos.get('EmailR')
    Id_Remitente = obtener_id_usuario(email_remitente, db)

    # Obtener Id del destinatario
    email_destinatario = datos.get('EmailD')
    Id_Destinatario = obtener_id_usuario(email_destinatario, db)

    costo = float(datos['tarifa'].replace('$', ''))
    nuevo_envio = Envio(
        Fecha_Entrega=datos.get('FechaR'),
        Costo=costo,
        Origen=datos.get('Origen'),
        Destino=datos.get('Destino'),
        id_Remitente=Id_Remitente,
        id_Destinatario=Id_Destinatario,
        Estatus=EstatusEnvio.EN_PROCESO
    )

    # Insertar en Envio
    db.add(nuevo_envio)
    db.flush()  # Asigna ID sin hacer commit total

    try:
        for paquete_json in paquetes_data:
            guia_code = ''.join([str(random.randint(0, 9)) for _ in range(18)])
            nuevo_paquete = Paquete(
                Peso=paquete_json.get('peso'),
                Largo=paquete_json.get('largo'),
                Alto=paquete_json.get('alto'),
                Ancho=paquete_json.get('ancho'),
                Guia=guia_code,
                id_Envio=nuevo_envio.id_Envio
            )

            # Insertar en Paquete
            db.add(nuevo_paquete)
            paquetes_creados.append({
                "id_Paquete": nuevo_paquete.id_Paquete,
                "Guia": nuevo_paquete.Guia
            })

        # Crear código de rastreo
        rastreo_code = ''.join([str(random.randint(0, 9)) for _ in range(20)])

        nuevo_rastreo = Rastreo(
            Codigo_Rastreo=rastreo_code,
            Num_Paquetes=len(paquetes_creados),
            id_Envio=nuevo_envio.id_Envio
        )

        # Insertar rastreo
        db.add(nuevo_rastreo)
        db.commit()

    except Exception as err:
        print(err)
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        db.close()

    return jsonify({"status": "success", "mensaje": "Datos procesados correctamente", "Rastreo_Code": rastreo_code}), 200


# CORRECIONES: En esta función probar con el metodo "GET" en vez de "POST"
# Función para rastrear un envio con el código de rastreo
@envios_bp.route("/rastrear/rastreo", methods=["POST"])
def rastrear_envio():
    datos = request.json  # Obtiene los datos del archivo json de la página web
    rastreo = datos.get("Rastreo")
    print("Número de rastreo:", rastreo)  # Imprime solo el número de rastreo para depuración

    db = get_session()

    # Alias de los usuarios tanto remitente como destinatario
    UsuarioRemitente = aliased(Usuario)
    UsuarioDestinatario = aliased(Usuario)

    # Query para retornar el rastreo de un envio con el codigo de rastreo
    resultado = (
        db.query(
            Envio.id_Envio,
            Rastreo.Num_Paquetes,
            Envio.Estatus,
            func.concat(UsuarioRemitente.Nombre, ' ', UsuarioRemitente.Apellido1, ' ',
                        UsuarioRemitente.Apellido2).label('Remitente'),
            func.concat(UsuarioDestinatario.Nombre, ' ', UsuarioDestinatario.Apellido1, ' ',
                        UsuarioDestinatario.Apellido2).label('Destinatario')
        )
        .join(Rastreo, Rastreo.id_Envio == Envio.id_Envio)
        .join(UsuarioRemitente, Envio.id_Remitente == UsuarioRemitente.id_Usuario)
        .join(UsuarioDestinatario, Envio.id_Destinatario == UsuarioDestinatario.id_Usuario)
        .filter(Rastreo.Codigo_Rastreo == rastreo)
        .all()
    )

    db.close()

    if resultado:
        # Si el resultado se encuentra, devuelve los datos de manera estructurada
        fila = resultado[0]
        return jsonify({
            "status": "success",
            "id_Envio": fila.id_Envio,
            "id_Paquete": fila.Num_Paquetes,
            "Estatus": fila.Estatus.value if hasattr(fila.Estatus, "value") else fila.Estatus,
            "Remitente": fila.Remitente,
            "Destinatario": fila.Destinatario,
        }), 200
    return jsonify({"status": "error", "mensaje": "Numero de rastreo no encontrado"}), 404