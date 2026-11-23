import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path

from awsiot import mqtt_connection_builder
from awscrt import mqtt

# Configuración del dispositivo
ENDPOINT = "a8q2sj0sl11na-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "estacion-iot-wsl"
TOPIC = "estacion-iot-wsl/telemetry"

# Ubicación de los certificados
BASE_DIR = Path(__file__).resolve().parent
CERT_DIR = BASE_DIR / "certificados"

CERTIFICATE = CERT_DIR / "device.pem.crt"
PRIVATE_KEY = CERT_DIR / "private.pem.key"
ROOT_CA = CERT_DIR / "AmazonRootCA1.pem"


def main():
    connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=str(CERTIFICATE),
        pri_key_filepath=str(PRIVATE_KEY),
        ca_filepath=str(ROOT_CA),
        client_id=CLIENT_ID,
        clean_session=True,
        keep_alive_secs=30
    )

    conectado = False

    try:
        print("Conectando con AWS IoT Core...")

        connection.connect().result(timeout=15)
        conectado = True

        print("Dispositivo conectado correctamente.\n")

        for numero in range(1, 6):
            temperatura = round(random.uniform(20, 30), 1)
            humedad = round(random.uniform(40, 80), 1)

            mensaje = {
                "device_id": CLIENT_ID,
                "sequence": numero,
                "temperature_c": temperatura,
                "humidity_pct": humedad,
                "status": "normal",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            future, packet_id = connection.publish(
                topic=TOPIC,
                payload=json.dumps(mensaje),
                qos=mqtt.QoS.AT_LEAST_ONCE
            )

            future.result(timeout=10)

            print(f"Lectura {numero}/5 enviada")
            print(f"Temperatura: {temperatura} °C")
            print(f"Humedad: {humedad} %")
            print("-" * 30)

            time.sleep(3)

    except Exception as error:
        print("Error de comunicación:", error)

    finally:
        if conectado:
            connection.disconnect().result(timeout=10)
            print("\nDispositivo desconectado.")


if __name__ == "__main__":
    main()
