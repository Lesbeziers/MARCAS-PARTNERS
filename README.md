# Marcas Partners

Herramienta interna para estampar logos de partner sobre carátulas de Movistar Plus+.
Arrastras un lote de imágenes, asignas marca y descargas un ZIP listo para entregar.

Funciona **abriendo `index.html` con doble clic**. No necesita servidor, ni instalación,
ni conexión a internet.

---

## Cómo se usa

1. **Inicio.** Arrastra las carátulas o haz clic para seleccionarlas.
2. **Selector de marcas** (columna izquierda):
   - `VARIOS PARTNERS` — asignas una marca distinta a cada carátula.
   - Un partner concreto — se aplica a todo el lote de una vez.
3. Navega entre carátulas con los botones `ANTERIOR` / `SIGUIENTE` o con las
   **flechas del teclado**.
4. `EXPORTAR` se activa cuando todas están en `OK`. Hasta entonces muestra
   cuántas faltan.

## Cómo agrupa las imágenes

El material llega de agencia sin convención fiable, así que **no se interpreta el
nombre**: solo se mide cuánto se parecen dos nombres entre sí.

Dos archivos son pareja si comparten casi todo el nombre, se diferencian solo al
final, y **uno es 16:9 y el otro 2:3**.

```
Anatomia_De_Un_Instante_001.jpg  ┐
Anatomia_De_Un_Instante_002.jpg  ┘  → una carátula, dos formatos
```

**El formato nunca se deduce del nombre, lo deciden los píxeles.** En un mismo pack
pueden convivir numeraciones contradictorias — `..._1`/`_2` donde 1 es el vertical,
y `..._20`/`_21` donde 0 es el horizontal — y fiarse del número pondría el logo en
el formato equivocado.

Si solo hay uno de los dos formatos, el que falta aparece como un hueco gris.

### Emparejado a mano

La heurística no acierta siempre, así que hay salida para los dos errores posibles:

- **Arrastra una carátula suelta sobre otra** para unirlas. Solo se iluminan los
  destinos válidos: si arrastras un horizontal, se encienden los verticales
  sueltos. Tú dices qué va con qué; cuál es cuál lo siguen decidiendo los píxeles.
- **La × de una fila emparejada la separa** en dos. Sirve tanto para deshacer un
  emparejado manual como para corregir un falso positivo del automático.

La marca ya asignada se conserva en ambas operaciones.

## Colocación de la marca

El logo va **a hueso contra la esquina superior derecha**. El aire necesario ya viene
dentro de cada SVG, calculado para que las cuatro marcas queden alineadas entre sí.

El tamaño se escala sobre el ancho del formato de referencia:

```
anchoLogo = anchoViewBox × (anchoImagen / anchoReferencia)
```

| Familia    | Referencia  | Ratio |
|------------|-------------|-------|
| Horizontal | 1920 × 1080 | 16:9  |
| Vertical   | 1200 × 1800 | 2:3   |

En ambos formatos de referencia el logo sale al mismo tamaño absoluto. Para medidas
mayores o menores, escala proporcional.

## Exportación

| Parámetro   | Valor                                              |
|-------------|----------------------------------------------------|
| Formato     | JPG siempre (un PNG de entrada se convierte)       |
| Nombre      | El del archivo original, intacto                   |
| Dimensiones | Las del original, exactas                          |
| Peso máximo | 1,5 MB por imagen                                  |
| Calidad     | La más alta que quepa bajo ese límite              |
| Entrega     | Un ZIP con todo                                    |

La calidad se busca por bisección: se mide el peso real del archivo y se ajusta hasta
clavar el valor más alto que entra en el límite. Si alguna imagen no llega a caber, o
hay que forzar mucho la compresión, la app lo avisa al terminar con la lista.

---

## Añadir un partner nuevo

1. Deja su SVG en `assets/img/` como archivo de referencia.
2. Añade una entrada en `assets/js/marcas.js` con el contenido del SVG pegado dentro
   del template literal `svg`.

No hay que tocar nada más: el desplegable, la previsualización y la exportación se
construyen a partir de esa lista.

El SVG va incrustado como texto y no enlazado por dos motivos: evita que los IDs
internos de unos SVG pisen los de otros, y permite exportar con la app abierta en
`file://` — un SVG leído del disco contaminaría el canvas y `toBlob()` dejaría de
funcionar.

---

## Estructura

```
index.html
assets/
├── css/
│   ├── fonts.css      Apercu Movistar
│   └── style.css
├── js/
│   ├── app.js         Toda la lógica
│   ├── marcas.js      Catálogo de partners
│   └── jszip.min.js   v3.10.1 (MIT)
├── img/               Logos de marca + cabecera
└── fonts/             Apercu Movistar
```

Sin build, sin dependencias que instalar, sin llamadas a internet.

---

## Aviso sobre los materiales incluidos

Esta es una **herramienta interna de Movistar Plus+**. El repositorio está
temporalmente en abierto como única forma de compartir la URL de pruebas
mientras se habilita el GitHub Enterprise corporativo; pasará a privado en
cuanto esté disponible.

El código es libre de reutilizar. **Los materiales gráficos no**:

- La familia tipográfica **Apercu Movistar** es una licencia comercial de
  Telefónica. Está aquí para que la herramienta funcione, no para su
  descarga ni uso fuera de este proyecto.
- Los logotipos de **Apple TV, Apple TV+, HBO Max y SkyShowtime** son
  marcas registradas de sus respectivos titulares, incluidas únicamente
  para el cometido de esta herramienta.
- La **cabecera y la identidad de Movistar Plus+** son propiedad de
  Telefónica.

Nada de lo anterior se publica bajo licencia abierta ni se cede para uso
de terceros.

La única dependencia externa es **JSZip 3.10.1** (licencia MIT), incluida
en `assets/js/`.
