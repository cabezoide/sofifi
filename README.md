# SOFIFI — Sintetizador de Ondas y Filtros Inmersivos en FPGA Integrada

*En inglés: Soundscapes On FPGA: Integrated Filters & Impulses.*

**Idiomas:** Español (fuente) · [English](README.en.md) · [简体中文](README.zh-CN.md)

![SOFIFI: el logotipo y la cara del pedal, con la OLED, seis mandos y dos pulsadores](docs/img/portada.png)

SOFIFI es un pedal de guitarra ambient (reverbs, shimmer, delays de cinta, freeze, granular)
implementado en una FPGA **Sipeed Tang Primer 25K** (Gowin GW5A-LV25).

**Versión:** `0.6` (la versión es la última fase cerrada; ver `docs/fases/estado_fases.csv`).

> Estado: **biblioteca de 43 programas y 344 presets** (Fase 06). Reverbs,
> delays, modulación, pitch, dinámica, filtros y textura. Los 43 dan en el RTL
> la misma salida que el modelo bit-exact (simulación). En la placa, a 100 MHz,
> está verificado el plate (Fase 05). Sigue el micro-looper y el granular
> (Fase 07). Todavía no suena con guitarra: falta el códec de audio (Fase 11).

## Escuchar los efectos (sin hardware)

1. Escuchar las demos de `demo_examples/`: una guitarra sintética (arpegio de
   Em9) pasada por cada programa, en Ogg Vorbis.
2. Procesar un WAV propio con un preset:

```bash
.venv/bin/sofifi presets hall                      # los presets de un programa
.venv/bin/sofifi render programas/hall.sasm guitarra.wav out/hall.wav --preset "Catedral" --cola 6
.venv/bin/sofifi render programas/shimmer.sasm guitarra.wav out/sh.wav --pot pot0=0.7 --pot pot3=0.6 --cola 6
.venv/bin/sofifi render programas/freeze.sasm guitarra.wav out/fz.wav --preset "Congelar suave" --freeze 1.5:8 --cola 8
```

| Familia | Programas |
|---|---|
| Reverb | plate, plate_vivo, hall, blackhole, cloud, bloom, spring, chorale, resonador, gated, reverb_inversa, infinite, freeze, freeze_givens, shimmer, shimmer_quinta, shimmer_energia |
| Delay | delay, cinta, bbd, pingpong, lluvia, ducking, reverse |
| Modulación | chorus, flanger, phaser, tremolo, vibrato, slicer |
| Pitch | octava, armonizador, doblador, escalera |
| Dinámica | compresor, puerta, swell |
| Filtro | autowah, filtro, ancho |
| Textura | saturacion, lofi, ringmod |

Qué hace cada uno, sus mandos y su coste: `docs/programas.md` (lo genera
`sofifi catalogo`). Los presets están en `presets/banco.toml`.

El WAV de entrada puede ser de 16, 24 o 32 bit y de cualquier frecuencia; se
remuestrea a 48 828 Hz. `sofifi asm` genera el microcódigo (`.hex` + `.json`) y
da los ciclos que gasta en el RTL.

## Qué se va a construir

- **Núcleo DSP microcodificado** al estilo Spin FV-1, ampliado: 2 048 instrucciones
  por muestra, acumulador de 48 bit e interpolación cúbica (ADR 0006). Los efectos
  son *programas*, no módulos RTL.
- **Todo el audio en BSRAM** (unos 0,9–1,4 s de líneas de retardo). La microSD guarda
  presets y grabaciones, pero no sirve de memoria de delay (ADR 0004).
- **fs = 48 828 Hz**, con reloj de sistema de 100 MHz: 2 048 ciclos por muestra
  exactos (ADR 0005).
- **Modelo de referencia bit-exact en Python**, que es el oráculo contra el que se
  valida el RTL (ADR 0003).

![¿Por qué escoger SOFIFI? Se puede leer, cambiar y comprobar bit a bit; frente al FV-1 gana en instrucciones y muestreo, y aún no suena con guitarra](docs/img/porque.png)

El estado del arte de 2026 y la hoja de ruta están en
`docs/investigacion/ESTADO_DEL_ARTE_2026.md`. Las infografías completas están en
`docs/infografias/`.

## Arranque

```bash
make install    # crea .venv con las herramientas del modelo y de la compuerta
make hooks      # instala el pre-push versionado
make ci         # compuerta local completa
```

La disciplina de trabajo está en `docs/SPEC_RAIZ.md`; el mapa para retomar en frío,
en `AGENTS.md`.

### Cadena EDA (Fase 02)

`make install` instala por pip toda la cadena abierta: Yosys y
nextpnr-himbaechel-gowin (YoWASP), apicula, openFPGALoader, verilator y cocotb.

```bash
make sim        # testbenches cocotb del RTL
make prog       # sintetiza hola_uart y lo carga en la SRAM de la Tang Primer 25K
make uart       # lee la UART del depurador (/dev/ttyUSB1) y exige "SOFIFI"
```

Para programar sin sudo hace falta la regla udev del depurador BL616
(`0403:6010`, grupo `plugdev`); se instala una vez con las instrucciones de
`scripts/udev/99-tang-primer-25k.rules`.

### Herramientas opcionales (compuertas blandas)

- `shellcheck`: lint de los scripts.

Si una herramienta falta, la compuerta lo dice (`WARN … NO CORRIÓ`); no finge un verde.

## Hardware

| Pieza | Estado |
|---|---|
| Tang Primer 25K + Dock | disponible |
| microSD de 64 GB (PMOD TF) | disponible |
| Códec I2S (PCM1808 + PCM5102A o Digilent Pmod I2S2) | **falta** (Fase 11) |
| MCP3208 + potenciómetros | falta (Fase 09; los botones de la Dock hacen de footswitch) |
| OLED SSD1306 de 128×64 | falta (Fase 10) |
| Buffer de entrada de guitarra | falta (provisional: cualquier pedal con buffer) |
| Módulo SDRAM de Sipeed | futuro (habilita looper y granular largos) |

Las fases que necesitan hardware que falta van al final del plan (09 a 12), de
modo que hasta la Fase 08 basta con la placa y la microSD.

![Las 13 fases: 7 cerradas, la siguiente y las que esperan hardware](docs/img/ruta.png)

## Documentación del hardware

- `BOM.md`: lista de compra del hardware, con enlaces.
- `SBOM.md`: qué hace cada componente del FPGA y con qué herramientas se construye.
- `docs/arquitectura_fpga.md`: la arquitectura del FPGA y cómo cambia fase a fase.
- `fails.md`: los fallos encontrados y cómo se resolvieron.
- `schematics/`: un esquemático PDF por cada módulo RTL, generado desde el Verilog.

## Idiomas

El español es la fuente canónica. Las traducciones llevan un sello con la huella
de la versión que traducen, y `scripts/check_i18n.py` impide que una traducción
diga estar al día cuando no lo está (ADR 0007). Los ADR, las specs de fase y los
mapas para agentes solo están en español.

## Licencia

MIT (ver `LICENSE`). Solo se porta código de terceros con licencia permisiva, y
cada origen se declara en `docs/terceros.yaml` (ADR 0002).
