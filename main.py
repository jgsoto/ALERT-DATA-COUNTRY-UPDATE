from bd_connection import conectar_db
from dotenv import load_dotenv
from ia_connection import IAGroqPais
from determinate_country import obtener_fechas, procesar_por_fecha    

load_dotenv()

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