from bd_connection import conectar_db
from datetime import timedelta, datetime
from dotenv import load_dotenv
from ia_connection import IAGroqPais
from determinate_country import obtener_iso3
from salert_repository import sincronizar_posts_por_dia, obtener_registros, actualizar_country
import time

load_dotenv()

def obtener_fechas(dias):
    hoy = datetime(2025, 6, 26).date()
    #hoy = datetime.now().date()
    return [hoy - timedelta(days=i) for i in range(dias)]

def procesar_por_fecha(cursor, fecha, ia_client):
    print("\nProcesando fecha:", fecha)

    registros = obtener_registros(cursor, fecha, fecha + timedelta(days=1))
    print("Registros encontrados:", len(registros))

    for id_registro, location, description in registros:

        iso3 = None

        # 1. location
        if location and location.strip():
            iso3 = obtener_iso3(location, ia_client)

        # 2. description
        if not iso3 and description and description.strip():

            es_geo = ia_client.es_texto_geografico(description)

            if es_geo:
                iso3 = ia_client.obtener_iso3_ia(description)

        valor_country = iso3 or "UNK"

        actualizar_country(cursor, id_registro, valor_country)

        time.sleep(0.2)

    actualizados = sincronizar_posts_por_dia(
        cursor, fecha, fecha + timedelta(days=1)
    )

    print("Posts sincronizados:", actualizados)

def main():
    conexion = conectar_db()
    cursor = conexion.cursor()

    ia_client = IAGroqPais()

    fechas = obtener_fechas(1)

    if not fechas:
        print("No hay registros pendientes")
        return

    try:
        for fecha in fechas:
            procesar_por_fecha(cursor, fecha, ia_client)
            conexion.commit()

        print("\nProceso terminado")

    except Exception as e:
        print("Error:", e)
        conexion.rollback()

    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    main()