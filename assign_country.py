from bd_connection import conectar_db
from datetime import timedelta, datetime
from dotenv import load_dotenv
from ia_connection import IAGroqPais
from determinate_country import obtener_iso3
from synchronize_post import sincronizar_posts_por_hora
import time

load_dotenv()

def obtener_fechas_pendientes(cursor, dias):

    cursor.execute(
        """
        SELECT MAX(DATE(extract_date))
        FROM public.salert_basic
        WHERE red BETWEEN 1 AND 3
          AND location IS NOT NULL
          AND location != ''
          AND country IS NULL
        """
    )

    resultado = cursor.fetchone()
    fecha_inicio = resultado[0] if resultado else None

    if not fecha_inicio:
        return []

    return [fecha_inicio - timedelta(days=i) for i in range(dias)]

def obtener_horas_con_registros(cursor, fecha):

    cursor.execute(
        """
        SELECT DISTINCT DATE_TRUNC('hour', extract_date)
        FROM public.salert_basic
        WHERE DATE(extract_date) = %s
        AND red BETWEEN 1 AND 3
        AND location IS NOT NULL
        AND location != ''
        AND country IS NULL
        ORDER BY 1 DESC
        """,
        (fecha,),
    )

    return [row[0] for row in cursor.fetchall()]

def procesar_locations():
    ia_client = IAGroqPais()
    conexion = conectar_db()
    cursor = conexion.cursor()

    dias_procesar = 5
    fechas = obtener_fechas_pendientes(cursor, dias_procesar)

    if not fechas:
        print("No hay registros pendientes")
        cursor.close()
        conexion.close()
        return

    try:
        for fecha in fechas:
            print("\nProcesando fecha:", fecha)

            horas = obtener_horas_con_registros(cursor, fecha)
            print("Horas con registros:", len(horas))

            for inicio in horas:
                
                fin = inicio + timedelta(hours=1)

                print("\nProcesando hora:", inicio)

                cursor.execute(
                    """
                    SELECT id, location
                    FROM public.salert_basic
                    WHERE red BETWEEN 1 AND 3
                      AND location IS NOT NULL
                      AND location != ''
                      AND country IS NULL
                      AND extract_date >= %s
                      AND extract_date < %s
                    ORDER BY extract_date DESC
                    """,
                    (inicio, fin),
                )

                registros = cursor.fetchall()
                print("Registros encontrados:", len(registros))

                for id_registro, location in registros:
                    iso3 = obtener_iso3(location, ia_client)
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

                conexion.commit()
                print(f"Commit realizado para la hora {inicio}")

                sincronizar_posts_por_hora(cursor, inicio, fin)
                
                conexion.commit()

        print("\nProceso terminado")

    except Exception as e:
        print("Error:", e)
        conexion.rollback()
        print("Rollback ejecutado")

    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    procesar_locations()