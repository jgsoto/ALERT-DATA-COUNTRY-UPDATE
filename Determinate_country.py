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