from bd_connection import conectar_db
from datetime import timedelta, datetime
from dotenv import load_dotenv
from ia_connection import IAGroqPais
from determinate_country import obtener_iso3
from salert_repository import sincronizar_posts_por_dia
import time

load_dotenv()

def obtener_fechas(dias):
    hoy = datetime(2025, 6, 26).date()
    #hoy = datetime.now().date()
    return [hoy - timedelta(days=i) for i in range(dias)]

def procesar_locations():
    ia_client = IAGroqPais()
    conexion = conectar_db()
    cursor = conexion.cursor()

    dias_procesar = 1
    fechas = obtener_fechas(dias_procesar)

    if not fechas:
        print("No hay registros pendientes")
        return

    try:
        for fecha in fechas:
            print("\nProcesando fecha:", fecha)

            cursor.execute(
                """
                SELECT id, location, description
                FROM public.salert_basic
                WHERE red BETWEEN 1 AND 3
                  AND country IS NULL
                  AND extract_date >= %s
                  AND extract_date < %s
                  AND (
                        (location IS NOT NULL AND location != '')
                        OR
                        (
                          (location IS NULL OR location = '')
                          AND (description IS NOT NULL AND description != '')
                        )
                      )
                ORDER BY extract_date DESC
                """,
                (fecha, fecha + timedelta(days=1)),
            )

            registros = cursor.fetchall()
            print("Registros encontrados:", len(registros))

            for id_registro, location, description in registros:

                iso3 = None

                if location and location.strip():
                    iso3 = obtener_iso3(location, ia_client)

                if not iso3 and description and description.strip():

                    es_geo = ia_client.es_texto_geografico(description)

                    if es_geo:
                        iso3 = ia_client.obtener_iso3_ia(description)

                valor_country = iso3 or "UNK"

                cursor.execute(
                    """
                    UPDATE public.salert_basic
                    SET country = %s
                    WHERE id = %s
                    """,
                    (valor_country, id_registro),
                )

                time.sleep(0.2)

            actualizados = sincronizar_posts_por_dia(
                cursor, fecha, fecha + timedelta(days=1)
            )
            print("Posts sincronizados:", actualizados)

            conexion.commit()

        print("\nProceso terminado")

    except Exception as e:
        print("Error:", e)
        conexion.rollback()

    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    procesar_locations()