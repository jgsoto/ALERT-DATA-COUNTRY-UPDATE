def sincronizar_posts_por_dia(cursor, inicio, fin):

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

def obtener_registros(cursor, fecha_inicio, fecha_fin):
    cursor.execute(
        """
        SELECT id, location, description
        FROM public.salert_basic
        WHERE red BETWEEN 1 AND 3
        AND country IS NULL
        AND extract_date >= %s
        AND extract_date < %s
        AND (COALESCE(location, '') != '' OR COALESCE(description, '') != '')
        ORDER BY extract_date DESC;
        """,
        (fecha_inicio, fecha_fin),
    )
    return cursor.fetchall()

def actualizar_country(cursor, id_registro, country):
    cursor.execute(
        """
        UPDATE public.salert_basic
        SET country = %s
        WHERE id = %s
        """,
        (country, id_registro),
    )