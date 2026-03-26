from datetime import timedelta, datetime
from salert_repository import sincronizar_posts_por_dia, obtener_registros, actualizar_country
import time
import pycountry
import re
import unicodedata

cache = {}

def quitar_acentos(texto):
    return "".join(
        c
        for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )

def limpiar_location(location):
    loc = location.lower()
    loc = loc.strip()
    loc = re.sub(r"[^\w\s,.-]", "", loc)
    loc = quitar_acentos(loc)
    loc = re.sub(r"\s+", " ", loc)
    loc = re.sub(r"\+?\d[\d\s\-]{6,}", "", loc)
    loc = re.sub(r"#\d+", "", loc)
    return loc

def es_texto_valido(location):
    if len(location.strip()) < 3:
        return False
    if re.search(r"http", location):
        return False
    if re.search(r"[0-9]{5,}", location):
        return False
    return True

def detectar_pais_directo(location):
    loc_lower = location.lower()

    for country in pycountry.countries:
        if country.name.lower() in loc_lower:
            return country.alpha_3

    return None

def obtener_iso3(location, ia_client):

    loc_limpia = limpiar_location(location)
    
    if loc_limpia in cache:
        return cache[loc_limpia]

    if not es_texto_valido(loc_limpia):
        cache[loc_limpia] = None
        return None

    iso3_directo = detectar_pais_directo(loc_limpia)

    if iso3_directo:
        cache[loc_limpia] = iso3_directo
        return iso3_directo

    iso3 = ia_client.obtener_iso3_ia(loc_limpia)

    cache[loc_limpia] = iso3

    return iso3

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