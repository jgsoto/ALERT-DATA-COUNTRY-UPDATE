from datetime import timedelta

def sincronizar_posts_por_hora(cursor, inicio, fin):

    cursor.execute(
        """
        UPDATE public.salert_post_temp p
        SET pais = b.country
        FROM public.salert_basic b
        WHERE p.page_id = b.id
        AND p.pais IS NULL
        AND b.country IS NOT NULL
        AND b.extract_date >= %s
        AND b.extract_date < %s
        """,
        (inicio, fin),
    )

    return cursor.rowcount

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