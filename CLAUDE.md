# Marcas Partners — guía de trabajo

Herramienta interna de **Movistar Plus+** para estampar logos de partner sobre
carátulas y exportarlas en un ZIP. Está **en producción y en uso real**.

El `README.md` explica *qué hace* la app. Este archivo explica *cómo trabajar en
ella*: las decisiones que no hay que deshacer, cómo verificar un cambio y cómo
se despliega.

---

## Rutas

| | |
|---|---|
| Proyecto (directorio de trabajo) | `/Volumes/MOVISTAR+/00 APPS/MARCAS DINÁMICAS/PROYECTO/MARCAS 1.0` |
| ZIP de despliegue generado | `…/PROYECTO/MarcasPartners_servidor.zip` |
| Material real de prueba | `/Volumes/MOVISTAR+/00 APPS/MARCAS DINÁMICAS/MATERIAL/PARTNERS_IMAGENES` |
| Repositorio | https://github.com/Lesbeziers/MARCAS-PARTNERS |
| Demo (GitHub Pages) | https://lesbeziers.github.io/MARCAS-PARTNERS/ |
| Producción | https://www.movistarplus.es/comunicacion/detallestecnicos/marcas_partners/MarcasPartners.html |

Es un volumen externo con espacios y acentos en la ruta: **entrecomillar siempre**.
Los archivos `._*` son metadatos de macOS, no son imágenes; están en `.gitignore`
y la app los filtra al cargar.

---

## Cómo trabajamos

**Idioma: español.** Conversación, comentarios del código, mensajes de commit y
textos de interfaz.

**Una pregunta cada vez.** Él explica por bloques y espera que se confirme lo
entendido en pocas líneas y se lance **una sola** pregunta, la que bloquea ahora
mismo. Lo que no bloquea todavía, se apunta y se espera: normalmente lo resuelve
él solo al seguir contando. Una batería de preguntas numeradas le rompe el hilo.

**Sus pantallazos son bocetos funcionales.** Valen la intención, la jerarquía y
la proporción; los detalles finos pueden estar mal y él lo sabe. Los diseña sobre
un lienzo de **1400 × 750**, dato que da para poder medir. El resultado siempre
**responsive**. Ante un detalle que no cuadra: señalarlo en una línea y seguir,
sin replicarlo a ciegas ni montar una pregunta.

**Verificar antes de decir que está hecho.** Es el método de toda la sesión
anterior y ha encontrado fallos reales. Medir, no estimar: abrir la app en el
navegador, ejercitar el flujo, leer la consola y la red. "Debería funcionar" no
vale.

**Donde no hay certeza, avisar.** Nunca inventar un resultado silencioso. Este
criterio ha decidido varios diseños: un emparejado dudoso se deja suelto, una
imagen que no cabe en el límite de peso se informa, un archivo ilegible se nombra.
Él prefiere ver el problema a que la app lo disimule.

**El botón de acción principal: atenuado e inactivo, nunca oculto.** Ocultarlo
esconde que la funcionalidad existe. `EXPORTAR` muestra además un contador
`(2/5)` mientras falten carátulas.

**Avisar solo cuando se pierde trabajo caro de rehacer.** Una modal que salta
siempre se cierra sin leer. Ver la tabla de la sección *Modal de confirmación*
del README.

---

## Decisiones técnicas que NO hay que deshacer

Todas tienen detrás un fallo real que costó encontrar. Si algo parece una
complicación innecesaria, probablemente sea una de estas.

### 1. Cero `blob:` en toda la app

El servidor corporativo aplica `img-src 'self' data:` — **sin `blob:`**. La app
usaba `blob:` para leer las medidas de cada archivo cargándolo en un `<img>`;
bajo esa política la carga fallaba, el archivo se descartaba y **el lote entero
quedaba vacío**. No era que no se vieran las imágenes: no se cargaba ninguna
carátula.

Ahora no interviene ninguna URL: los archivos se decodifican con
`createImageBitmap(File)`, y las previsualizaciones son `data:` reducidas a
1600 px de lado mayor.

**Única excepción:** `URL.createObjectURL` en `descargar()`, para el enlace de
descarga del ZIP. No es una imagen, la CSP no lo cubre, y está **verificado
funcionando en producción**.

### 2. Los SVG de las marcas van incrustados como texto en `marcas.js`

No enlazados. Dos motivos: los cuatro SVG usan los mismos IDs internos (`a`, `b`,
`c`…) y al incrustarlos juntos en el DOM los filtros de uno pisarían los de otro;
y un SVG leído del disco contaminaría el canvas con la app abierta en `file://`,
dejando `toBlob()` inservible.

Cada uno se convierte en su propia imagen `data:` independiente, lo que resuelve
ambas cosas.

### 3. El formato lo deciden los píxeles, nunca el nombre

En un mismo pack real conviven numeraciones **contradictorias**: `..._1`/`_2`
donde 1 es el vertical, y `..._20`/`_21` donde 0 es el **horizontal**. Deducir el
formato del número pondría el logo en el formato equivocado.

El nombre solo sirve para *agrupar*; el formato sale de `ancho > alto`.

### 4. El emparejado es una hipótesis que valida el ratio

Dos archivos son pareja si comparten casi todo el nombre **y** uno es 16:9
mientras el otro es 2:3. Si el grupo no da exactamente 1 H + 1 V, no se empareja:
se deja suelto. Ante un empate exacto tampoco se elige al azar.

No hay ninguna regla sobre la estructura del nombre, a propósito: el material
llega de agencias distintas sin convención fiable. Funciona igual con
`3287217_HBO MAX_DUNE PARTE DOS1` que con `Anatomia_De_Un_Instante_001`.

**Lo suelto es la señal, no un residuo.** Hubo un archivo `copia` que resultó ser
una imagen de test con dos logos superpuestos; la app no podía saberlo, pero al
no emparejarlo obligó a mirarlo. Se descartó añadir un botón de eliminar por eso:
limpiaría la lista y se perdería el aviso.

### 5. El logo va a hueso contra la esquina, sin margen calculado

El aire ya viene dentro de cada SVG. Está medido: **las cuatro marcas tienen
exactamente 82 px de aire a la derecha** y sus centros ópticos verticales caen
en ~110 px. Añadir un margen rompería esa alineación.

Escala: `anchoLogo = anchoViewBox × (anchoImagen / anchoReferencia)`, con
referencia 1920 para las 16:9 y 1200 para las 2:3. En ambos formatos de
referencia el logo sale al **mismo tamaño absoluto**.

### 6. La exportación sale siempre del original

`componer()` decodifica el archivo original con `createImageBitmap`, **nunca la
previsualización reducida**. La calidad JPG se busca por bisección hasta clavar
el valor más alto que entra en 1,5 MB.

Un dato de cuando se diseñó: el archivo `copia` del pack real **no era un
duplicado exacto** (MD5 distinto), así que descartar duplicados por checksum no
habría funcionado.

### 7. `?v=FECHA` en las rutas del HTML

El servidor entrega CSS y JS con **14 días de caché sin revalidar**; el HTML
revalida cada 2 horas. Sin versionar, una actualización no la vería nadie hasta
dos semanas después. Esto costó media hora de diagnóstico en su día.

Funciona **retroactivamente**: basta con que un despliegue incluya el `?v=`
nuevo para que todos reciban los archivos frescos en un par de horas, aunque
lleven días con la versión vieja.

---

## Cómo verificar un cambio

No hay build ni tests. La verificación es ejecutar la app y medir.

**1. Servidor local replicando la CSP de producción.** El sandbox del preview no
puede leer el volumen externo, así que hay que copiar el proyecto a `/tmp` y
servirlo desde ahí. Un servidor que mande la CSP real reproduce el entorno
corporativo:

```bash
curl -sI https://www.movistarplus.es/comunicacion/detallestecnicos/marcas_partners/MarcasPartners.html | grep -i '^content-security-policy:'
```

Las tres directivas que aplica son `default-src`, `img-src 'self' data:` y
`font-src 'self' data:`. Conviene mandar también `Cache-Control: no-store`, o el
navegador servirá el JS antiguo y se perderá tiempo creyendo que el arreglo no
funciona (pasó dos veces).

**2. Imágenes de prueba sintéticas.** Generarlas con canvas dentro de la propia
página y pasarlas a `cargarArchivos()`, usando los **nombres y medidas reales**
del pack de `MATERIAL/PARTNERS_IMAGENES`. Así se prueba el emparejado contra
material de verdad sin depender de que el navegador pueda leer el volumen.

**3. Comprobar el ZIP exportado**, no solo que la descarga se dispare:
interceptar `descargar()`, abrir el ZIP con `JSZip.loadAsync` y verificar nombres,
medidas y peso de cada archivo.

---

## Despliegue

**Subir es caro.** No es arrastrar un archivo: implica subir a otra planta,
molestar a una compañera, encender el único PC del área con acceso al FTP, subir,
bajar a comprobarlo en el Mac y acordarse de restaurar la sesión de ella.

**No proponer despliegues sueltos.** Agrupar los cambios y subir una vez. Si algo
funciona y la mejora no es urgente, esperar al siguiente viaje es la decisión
correcta.

El paquete se genera con:

```bash
python3 empaquetar.py
```

Ese script hace lo que el servidor necesita y el repositorio no: renombra
`index.html` a `MarcasPartners.html` (ese servidor no toma el index como landing),
pone la fecha de hoy en las rutas `?v=` y deja fuera los `.eot` y `.ttf`, que
`fonts.css` no referencia.

---

## Estado actual

| | |
|---|---|
| Producción | Funcionando. Carga, emparejado y exportación verificados por él |
| Versión desplegada | **23/10/2026, sin rutas versionadas** |
| Repositorio | Al día, `main` sincronizado |
| GitHub Pages | Activo |

### Pendiente

**El ZIP con las rutas versionadas sigue sin subir.** Producción funciona, pero
sin el blindaje de caché: la próxima actualización no la vería nadie en 14 días.
Como el versionado funciona retroactivamente, basta con incluirlo en el siguiente
despliegue, sea cuando sea. No merece un viaje al FTP solo para eso.

**El repositorio es público temporalmente.** Contiene las Apercu Movistar y los
logos de los partners. No es descuido: en el plan gratuito, GitHub Pages solo
funciona con repositorios públicos, y necesitaba la URL para enseñar los avances.
Pasará a privado cuando le den el GitHub Enterprise corporativo. Mitigaciones ya
puestas: `noindex, nofollow` en el HTML y un aviso de propiedad en el README.
**No volver a sacar el tema**: está decidido y razonado.
