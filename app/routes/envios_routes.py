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
from app.models.destinatario import Destinatario

envios_bp = Blueprint ('envios', __name__)

# Obtener el id del usuario por el correo
def obtener_id_usuario(email_usuario, session):
    usuario = session.query(Usuario).filter_by(Email=email_usuario).first()
    if not usuario:
        raise ValueError("Usuario no encontrado")
    return usuario.id_Usuario

# Función que obtiene o crea un destinatario nuevo
def obtener_o_crear_destinatario(datos_destinatario, session):
    """
    Busca un destinatario por email. Si existe, lo retorna.
    Si no existe, crea uno nuevo.
    """
    email = datos_destinatario.get('EmailD')

    # Buscar destinatario existente
    destinatario = session.query(Destinatario).filter_by(Email=email).first()

    if destinatario:
        # Si existe, actualizar sus datos (opcional)
        destinatario.Nombre = datos_destinatario.get('NombreD')
        destinatario.Apellido1 = datos_destinatario.get('ApellidoD')
        destinatario.Apellido2 = datos_destinatario.get('Apellido2D')
        destinatario.Telefono = datos_destinatario.get('TelefonoD')
        return destinatario.id_Destinatario
    else:
        # Si no existe, crear nuevo destinatario
        nuevo_destinatario = Destinatario(
            Nombre=datos_destinatario.get('NombreD'),
            Apellido1=datos_destinatario.get('ApellidoD'),
            Apellido2=datos_destinatario.get('Apellido2D'),
            Email=email,
            Telefono=datos_destinatario.get('TelefonoD')
        )
        session.add(nuevo_destinatario)
        session.flush()  # Obtener el ID sin hacer commit
        return nuevo_destinatario.id_Destinatario


# Función para realizar envios.
@envios_bp.route('/Cotizar/Envio', methods=['POST'])
def Envios():
    datos = request.json
    paquetes_data = datos.get('paquetes', [])
    paquetes_creados = []

    db = get_session()

    try:
        # Obtener Id del remitente
        email_remitente = datos.get('EmailR')
        Id_Remitente = obtener_id_usuario(email_remitente, db)

        # Obtener o crear destinatario
        Id_Destinatario = obtener_o_crear_destinatario({
            'NombreD': datos.get('NombreD'),
            'ApellidoD': datos.get('ApellidoD'),
            'Apellido2D': datos.get('Apellido2D'),
            'EmailD': datos.get('EmailD'),
            'TelefonoD': datos.get('TelefonoD')
        }, db)

        # Procesar el costo
        costo = float(datos['tarifa'].replace('$', '').replace(',', ''))

        # Usar la fecha calculada que viene del frontend
        fecha_entrega_str = datos.get('FechaEntrega')  # Formato: 'DD/MM/YYYY'

        # Convertir de DD/MM/YYYY a objeto date
        if fecha_entrega_str:
            from datetime import datetime
            fecha_entrega = datetime.strptime(fecha_entrega_str, '%d/%m/%Y').date()
        else:
            fecha_entrega = None

        # Crear envío
        nuevo_envio = Envio(
            Fecha_Entrega=fecha_entrega,  # Usar fecha calculada
            Costo=costo,
            Origen=datos.get('Origen'),
            Direccion_Origen=datos.get('DireccionOrigen'),
            Destino=datos.get('Destino'),
            Direccion_Destino=datos.get('DireccionDestino'),
            id_Remitente=Id_Remitente,
            id_Destinatario=Id_Destinatario,
            Estatus=EstatusEnvio.EN_PROCESO
        )

        db.add(nuevo_envio)
        db.flush()

        # Crear paquetes
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

        db.add(nuevo_rastreo)
        db.commit()

        return jsonify({
            "status": "success",
            "mensaje": "Envío registrado correctamente",
            "Rastreo_Code": rastreo_code,
            "id_Envio": nuevo_envio.id_Envio,
            "fecha_entrega": fecha_entrega_str,
            "paquetes": paquetes_creados
        }), 200

    except ValueError as ve:
        db.rollback()
        print(f"Error de validación: {ve}")
        return jsonify({"status": "error", "mensaje": str(ve)}), 400
    except Exception as err:
        db.rollback()
        print(f"Error general: {err}")
        return jsonify({"status": "error", "mensaje": "Error al procesar la solicitud"}), 500
    finally:
        db.close()


# CORRECIONES: En esta función probar con el metodo "GET" en vez de "POST"
# Función para rastrear un envio con el código de rastreo
@envios_bp.route("/rastrear/rastreo", methods=["POST"])
def rastrear_envio():
    datos = request.json  # Obtiene los datos del archivo json de la página web
    rastreo = datos.get("Rastreo")
    print("rastreo:", rastreo, type(rastreo)) # Imprime solo el número de rastreo para depuración

    db = get_session()

    # Alias de los usuarios tanto remitente como destinatario
    UsuarioRemitente = aliased(Usuario)
    UsuarioDestinatario = aliased(Destinatario)

    # Query para retornar el rastreo de un envio con el codigo de rastreo
    resultado = (
        db.query(
            Envio.id_Envio,
            Rastreo.Num_Paquetes,
            Envio.Estatus,
            Envio.Fecha_Entrega,
            Envio.Direccion_Origen,
            Envio.Direccion_Destino,
            func.concat(
                UsuarioRemitente.Nombre, ' ',
                UsuarioRemitente.Apellido1, ' ',
                UsuarioRemitente.Apellido2
            ).label('Remitente'),
            func.concat(
                UsuarioDestinatario.Nombre, ' ',
                UsuarioDestinatario.Apellido1, ' ',
                UsuarioDestinatario.Apellido2
            ).label('Destinatario')
        )
        .join(Rastreo, Rastreo.id_Envio == Envio.id_Envio)
        .join(UsuarioRemitente, Envio.id_Remitente == UsuarioRemitente.id_Usuario)
        .join(UsuarioDestinatario, Envio.id_Destinatario == UsuarioDestinatario.id_Destinatario)
        .filter(func.trim(Rastreo.Codigo_Rastreo) == rastreo)
        .first()
    )

    db.close()

    if resultado:
        # Si el resultado se encuentra, devuelve los datos de manera estructurada
        return jsonify({
            "status": "success",
            "id_Envio": resultado.id_Envio,
            "id_Paquete": resultado.Num_Paquetes,
            "Estatus": resultado.Estatus.value if hasattr(resultado.Estatus, "value") else resultado.Estatus,
            "Remitente": resultado.Remitente,
            "Destinatario": resultado.Destinatario,
            "Fecha_Entrega": resultado.Fecha_Entrega.isoformat() if resultado.Fecha_Entrega else None,
            "Direccion_Origen": resultado.Direccion_Origen,
            "Direccion_Destino": resultado.Direccion_Destino
        }), 200
    return jsonify({"status": "error", "mensaje": "Numero de rastreo no encontrado"}), 404