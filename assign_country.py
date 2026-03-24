from bd_connection import conectar_db
from datetime import timedelta, datetime
from dotenv import load_dotenv
from ia_connection import IAGroqPais
from determinate_country import obtener_iso3
from salert_repository import sincronizar_posts_por_hora
import time

load_dotenv()

def obtener_fechas_pendientes(dias):
    hoy = datetime.now().date()
    return [hoy - timedelta(days=i) for i in range(dias)]

def obtener_horas_hasta_ahora(fecha):
    ahora = datetime.now()
    
    if fecha == ahora.date():
        max_hora = ahora.hour
    else:
        max_hora = 23

    return [
        datetime.combine(fecha, datetime.min.time()) + timedelta(hours=i)
        for i in range(max_hora + 1)
    ]

def procesar_locations():
    ia_client = IAGroqPais()
    conexion = conectar_db()
    cursor = conexion.cursor()

    dias_procesar = 5
    fechas = obtener_fechas_pendientes(dias_procesar)

    if not fechas:
        print("No hay registros pendientes")
        cursor.close()
        conexion.close()
        return

    try:
        for fecha in fechas:
            print("\nProcesando fecha:", fecha)

            horas = obtener_horas_hasta_ahora(fecha)
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

                actualizados = sincronizar_posts_por_hora(cursor, inicio, fin)
                print("Posts sincronizados:", actualizados)
                
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