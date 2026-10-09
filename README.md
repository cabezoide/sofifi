# SOFIFI — Sintetizador de Ondas y Filtros Inmersivos en FPGA Integrada

*En inglés: Soundscapes On FPGA: Integrated Filters & Impulses.*

**Idiomas:** Español (fuente) · [English](README.en.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

![SOFIFI: el logotipo y la cara del pedal, con la OLED, seis mandos y dos pulsadores](docs/img/portada.png)

SOFIFI es un pedal de guitarra ambient de código abierto. Funciona en una FPGA
**Sipeed Tang Primer 25K** (Gowin GW5A-LV25). Cada efecto es un programa de
texto que ejecuta un núcleo DSP propio.

**Versión:** `0.7` (la versión es la última fase cerrada; ver `docs/fases/estado_fases.csv`).

## Estado

| Qué | Estado |
|---|---|
| Biblioteca | **86 programas y 688 presets** en 8 familias (Fase 07) |
| Dos efectos a la vez | **24 cadenas**: 18 caben hoy y 6 esperan la SDRAM (`presets/cadenas.toml`, ADR 0013) |
| Igualdad con el modelo, en simulación | los 86 programas y las 18 cadenas que caben dan en el RTL los mismos bits que el modelo |
| Igualdad con el modelo, en la placa | 50 de 50: 41 programas y 9 cadenas, con el núcleo de la Fase 07 (MED-16, 2026-10-08) |
| Núcleo | segmentado en orden (ADR 0014): gasta 1,6 veces menos ciclos; sin errores en la placa a 125 MHz (3 de 3) y a 133,3 MHz (2 de 2); trabaja a 100 MHz |
| En curso | **Fase 08, microSD:** el banco, el controlador SD y el top `prueba_sd` funcionan en simulación. Falta la prueba con la tarjeta real (`docs/microsd.md`) |
| Audio con guitarra | **todavía no**: falta el códec I2S (Fase 11) |

## Escuchar los efectos sin hardware

1. Escuchar las demos de `demo_examples/`. Son una guitarra sintética (un
   arpegio de Em9) pasada por cada programa, en Ogg Vorbis.
2. Procesar un WAV propio con un preset:

```bash
.venv/bin/sofifi presets hall                      # lista los presets de un programa
.venv/bin/sofifi render programas/hall.sasm guitarra.wav out/hall.wav --preset "Catedral" --cola 6
.venv/bin/sofifi render programas/shimmer.sasm guitarra.wav out/sh.wav --pot pot0=0.7 --pot pot3=0.6 --cola 6
.venv/bin/sofifi render programas/freeze.sasm guitarra.wav out/fz.wav --preset "Congelar suave" --freeze 1.5:8 --cola 8
```

- `--preset` toma los mandos de `presets/banco.toml`. Un `--pot` posterior cambia uno.
- `--freeze INICIO:FIN` pulsa el footswitch entre dos tiempos, en segundos.
- `--cola` añade segundos de silencio al final, para oír la cola.
- El WAV de entrada puede ser de 16, 24 o 32 bit y de cualquier frecuencia. El
  modelo lo remuestrea a 48 828 Hz.

| Familia | Programas |
|---|---|
| Reverb (26) | plate, plate_vivo, hall, blackhole, cloud, bloom, spring, chorale, resonador, gated, reverb_inversa, infinite, freeze, freeze_givens, shimmer, shimmer_quinta, shimmer_energia, shimmer_grave, shimmer_escondido, ensemble, marea, shoegaze, sostenido, dinamica, baldosa, semilla |
| Delay (21) | delay, cinta, bbd, pingpong, lluvia, ducking, reverse, bruma, tambor, oscilador, enjambre, probabilidad, dados, aureo, estelar, lata, deriva, eco_casero, dos_ecos, frenada, compas |
| Modulación (11) | chorus, flanger, phaser, tremolo, vibrato, slicer, armonico, desplazador, dimension, orilla, vibe |
| Pitch (8) | octava, armonizador, doblador, escalera, arcoiris, acople, arpegio, espiral |
| Dinámica (6) | compresor, puerta, swell, violin, arco, swell_ritmico |
| Looper (6) | looper, erosion, mosaico, relevo, resbalon, tartamudeo |
| Textura (5) | saturacion, lofi, ringmod, granular, viento |
| Filtro (3) | autowah, filtro, ancho |

`docs/programas.md` dice qué hace cada programa, qué mandos tiene y cuánto
cuesta. Lo genera `sofifi catalogo`.

## Cómo funciona

- **Núcleo DSP microcodificado**, al estilo del Spin FV-1 y ampliado: hasta
  2 048 instrucciones por muestra, acumulador de 48 bit e interpolación cúbica
  (ADR 0006). Un efecto nuevo es un fichero `.sasm`; el RTL no cambia.
- **Todo el audio en la BSRAM de la FPGA:** 43 008 palabras, unos 0,88 s. La
  microSD guarda presets y grabaciones, pero no sirve de memoria de retardo,
  porque tiene picos de escritura de 250 ms (ADR 0004).
- **Looper y granular:** una región de 32 768 palabras (0,67 s) con direcciones
  absolutas, que el puntero circular no mueve. La leen y escriben `RDAA` y
  `WRAA` (ADR 0009). Con la SDRAM llegarán loops más largos.
- **fs = 48 828 Hz:** un reloj de 100 MHz da 2 048 ciclos exactos por muestra (ADR 0005).
- **Modelo de referencia bit-exact en Python.** El RTL debe dar los mismos bits
  que el modelo, muestra a muestra (ADR 0003).
- **Coste real:** el núcleo está segmentado en orden (ADR 0014). Una
  instrucción solo espera si lee un resultado que aún no está listo, como el
  del ACC. Un programa gasta de 185 a 1 620 ciclos de los 2 048. `sofifi asm`
  da los ciclos de un programa.

![¿Por qué escoger SOFIFI? Se puede leer, cambiar y comprobar bit a bit; frente al FV-1 gana en instrucciones y muestreo, y aún no suena con guitarra](docs/img/porque.png)

Las infografías completas están en `docs/infografias/`. El estado del arte de
2026 y la hoja de ruta están en `docs/investigacion/ESTADO_DEL_ARTE_2026.md`.

## Arranque

1. Crear el entorno con las herramientas del modelo, de la compuerta y de la FPGA:
   `make install`.
2. Instalar el pre-push del repositorio: `make hooks`.
3. Pasar la compuerta local completa: `make ci`.

`docs/SPEC_RAIZ.md` define la disciplina de trabajo. `AGENTS.md` es el mapa
para retomar el proyecto en frío.

### Cadena EDA

`make install` instala por pip toda la cadena abierta: Yosys y
nextpnr-himbaechel-gowin (YoWASP), apicula, openFPGALoader, verilator y cocotb.

```bash
make sim           # testbenches cocotb del RTL
make prog          # sintetiza hola_uart y lo carga en la SRAM de la Tang Primer 25K
make uart          # lee la UART del depurador (/dev/ttyUSB1) y exige "SOFIFI"
make esquematicos  # regenera los esquemáticos PDF del RTL
make hil HIL=hall  # carga un programa o una cadena en la placa y lo compara con el modelo
```

Para programar sin sudo hace falta la regla udev del depurador BL616
(`0403:6010`, grupo `plugdev`). Se instala una vez, con las instrucciones de
`scripts/udev/99-tang-primer-25k.rules`.

### Herramientas opcionales

| Herramienta | Para qué |
|---|---|
| `shellcheck` | lint de los scripts (compuerta blanda) |
| Node.js y chrome-headless-shell | esquemáticos (`make esquematicos`) y capturas de las infografías |

Si falta una herramienta, la compuerta lo dice (`NO CORRIÓ`). No da un verde falso.

## Hardware

| Pieza | Estado |
|---|---|
| Tang Primer 25K + Dock | disponible |
| microSD de 64 GB y módulo Sipeed PMOD TF | disponible; falta probar la tarjeta en la placa (Fase 08) |
| Códec I2S (PCM1808 + PCM5102A o Digilent Pmod I2S2) | **falta** (Fase 11) |
| MCP3208 + potenciómetros | falta (Fase 09; los botones de la Dock hacen de footswitch) |
| OLED SSD1306 de 128×64 | falta (Fase 10) |
| Buffer de entrada de guitarra | falta (provisional: cualquier pedal con buffer) |
| Módulo SDRAM de Sipeed | futuro (para un looper y un granular largos) |

Las fases que necesitan el hardware que falta van al final (09 a 12). Hasta la
Fase 08 bastan la placa y la microSD.

![Las 13 fases: 8 cerradas, la siguiente y las que esperan hardware](docs/img/ruta.png)

## Documentación

| Documento | Qué contiene |
|---|---|
| `docs/programas.md` | los 86 programas: qué hacen, mandos, presets y coste |
| `presets/banco.toml` | los 688 presets |
| `docs/arquitectura_fpga.md` | la arquitectura del FPGA y cómo cambia en cada fase |
| `schematics/` | un esquemático PDF de cada módulo RTL, generado desde el Verilog |
| `presets/cadenas.toml` | las 24 cadenas de dos programas |
| `docs/microsd.md` | cómo escribir el banco de programas en la microSD y probarlo en la placa |
| `docs/EXTENDING.md` | cómo añadir un programa, un preset, una cadena, una instrucción, un módulo RTL o una compuerta |
| `BOM.md` | lista de compra del hardware, con enlaces |
| `SBOM.md` | qué hace cada componente del FPGA y con qué herramientas se construye |
| `fails.md` | los fallos encontrados: síntoma, causa, resolución y lección |

## Scripts

Los scripts de `scripts/` construyen, prueban y miden el proyecto. La guía
[docs/scripts.md](docs/scripts.md) dice qué hace cada uno, cuándo usarlo y con
qué opciones.

## Idiomas

- El español es la fuente.
- La documentación pública y técnica tiene traducción al inglés, al chino
  simplificado y al japonés: este README, las infografías, el catálogo, las
  guías de demos y de esquemáticos, la arquitectura, `EXTENDING`, `BOM`, `SBOM`
  y `fails`.
- Cada traducción lleva un sello con la huella de la versión que traduce.
  `scripts/check_i18n.py` impide que una traducción diga estar al día cuando no
  lo está (ADR 0007).
- Los ADR, las specs de fase, la investigación y los mapas para agentes están
  solo en español.

## Licencia

MIT (ver `LICENSE`). Solo se porta código de terceros con licencia permisiva, y
cada origen se declara en `docs/terceros.yaml` (ADR 0002).
