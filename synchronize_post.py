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

    actualizados = cursor.rowcount

    print("Posts sincronizados:", actualizados)

    return actualizados