#!/usr/bin/env python3
"""Genera el ZIP para el servidor de comunicacion.movistar.

    python3 empaquetar.py

Deja el paquete en  ../MarcasPartners_servidor.zip  con una carpeta
MarcasPartners/ lista para soltar en el FTP.

Hace tres cosas que el repositorio no necesita pero el servidor sí:

1. Renombra index.html a MarcasPartners.html. Ese servidor no toma el
   index como página por defecto. Se incluye además un index.html mínimo
   que redirige, por si alguien abre la carpeta por su raíz.

2. Pone la fecha de hoy en las rutas ?v= del HTML. El servidor entrega
   CSS y JS con catorce días de caché sin revalidar, así que sin cambiar
   ese número nadie vería la actualización hasta dos semanas después.
   Automatizarlo evita el único paso manual que se puede olvidar.

3. Deja fuera los .eot y .ttf. fonts.css solo referencia woff2 y woff,
   de modo que serían 2,6 MB que nadie descarga nunca. Siguen en el
   repositorio como archivo de referencia.
"""

import os
import re
import sys
import zipfile
from datetime import date

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(os.path.dirname(RAIZ), "MarcasPartners_servidor.zip")
VERSION = date.today().strftime("%Y%m%d")

REDIRECCION = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta http-equiv="refresh" content="0; url=MarcasPartners.html">
<link rel="canonical" href="MarcasPartners.html">
<title>Marcas Partners · Movistar Plus+</title>
</head>
<body>
<!-- El archivo real es MarcasPartners.html, porque este servidor no toma
     index.html como landing. Esto solo existe para que quien abra la
     carpeta por su raíz acabe igualmente en la herramienta. -->
<p>Redirigiendo a <a href="MarcasPartners.html">MarcasPartners.html</a>…</p>
</body>
</html>
"""


def versionar(html):
    """Pone ?v=HOY en cada ruta de assets, la tuviera ya o no."""
    def sustituir(m):
        atributo, ruta = m.group(1), m.group(2).split("?")[0]
        # El SVG de cabecera cambia de nombre cuando cambia, no hace falta.
        if ruta.endswith(".svg"):
            return f'{atributo}="{ruta}"'
        return f'{atributo}="{ruta}?v={VERSION}"'

    return re.sub(r'(href|src)="(assets/[^"]+)"', sustituir, html)


def fuentes_referenciadas():
    css = open(os.path.join(RAIZ, "assets/css/fonts.css"), encoding="utf-8").read()
    rutas = set()
    for u in re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", css):
        if u.startswith(("data:", "http")):
            continue
        rutas.add(os.path.normpath(os.path.join("assets/css", u)))
    return sorted(rutas)


def main():
    os.chdir(RAIZ)

    archivos = [
        "assets/css/fonts.css",
        "assets/css/style.css",
        "assets/js/app.js",
        "assets/js/marcas.js",
        "assets/js/jszip.min.js",
    ]
    archivos += sorted(
        f"assets/img/{f}" for f in os.listdir("assets/img")
        if f.endswith(".svg") and not f.startswith("._")
    )
    archivos += fuentes_referenciadas()

    faltan = [p for p in archivos + ["index.html"] if not os.path.exists(p)]
    if faltan:
        sys.exit("Faltan archivos:\n  " + "\n  ".join(faltan))

    html = versionar(open("index.html", encoding="utf-8").read())

    # Red de seguridad: que no se cuele una llamada a internet.
    externas = [u for u in re.findall(r'(?:href|src)="(https?://[^"]+)"', html)]
    if externas:
        sys.exit("El HTML apunta fuera, revísalo:\n  " + "\n  ".join(externas))

    if os.path.exists(SALIDA):
        os.remove(SALIDA)

    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("MarcasPartners/MarcasPartners.html", html)
        z.writestr("MarcasPartners/index.html", REDIRECCION)
        for p in archivos:
            z.write(p, f"MarcasPartners/{p}")

    peso = os.path.getsize(SALIDA) / 1048576
    print(f"ZIP listo: {SALIDA}")
    print(f"  {len(archivos) + 2} archivos · {peso:.2f} MB · rutas con ?v={VERSION}")
    print()
    print("  Subir al FTP sustituyendo el contenido de")
    print("  comunicacion/detallestecnicos/marcas_partners/")


if __name__ == "__main__":
    main()
