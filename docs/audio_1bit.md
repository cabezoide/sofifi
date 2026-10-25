# Salida de audio de 1 bit

Cómo suena el pedal en la placa sin el códec I2S (Fase 13, ADR 0015). Un pin, dos resistencias y dos condensadores.

## La idea

El reloj es 2 048 veces la frecuencia de muestreo (ADR 0005). Con ese sobremuestreo, un solo pin lleva audio:

```
muestra S.23 a fs ─► recorte ±13/16 ─► CIC S=2, R=32 ─► mantenimiento ×64 ─► Σ∆ 2.º orden ─► pin
                                          32·fs              100 MHz            1 bit/ciclo
```

- El **interpolador CIC** aparta las imágenes de la muestra: la primera queda en 1,5625 MHz.
- El **modulador sigma-delta** aparta el ruido de cuantificación hacia los megahercios.
- El **filtro RC** quita todo lo que está por encima del audio. Sin él, el pin solo da una onda cuadrada.

## Medidas en el modelo

| Entrada | SNR en banda (0-20 kHz) |
|---|---|
| −2 dBFS | 117 dB |
| −6 dBFS | 113 dB |
| −12 dBFS | 107 dB |
| −20 dBFS | 62 dB |

La cadena es mejor que el pin: la calidad real la fijan el filtro, el jitter del pin y la masa de la placa. Es una salida para oír y medir, no la salida del pedal (ADR 0015).

## El filtro

> **Advertencia.** No se conectan unos auriculares al pin. El pin da 0 o 3,3 V, y sin filtro ni atenuación el nivel es peligroso para el oído y para el equipo.

Dos secciones RC, un condensador de bloqueo y un divisor. Valores calculados, aún sin medir en la placa [INF]:

| Pieza | Valor | Para qué |
|---|---|---|
| R1 | 1 kΩ | primera sección; con C1 corta en 23,4 kHz |
| C1 | 6,8 nF | |
| R2 | 1 kΩ | segunda sección; a 1,5625 MHz atenúa unos 73 dB |
| C2 | 6,8 nF | |
| C3 | 1 µF | bloquea la componente continua de 1,65 V |
| R3 | 10 kΩ | descarga de C3; con C3 corta en 16 Hz |
| R4 y R5 | 2,2 kΩ y 220 Ω | divisor por 11: de 2,7 V a 0,24 V de pico a pico, nivel de entrada de amplificador |

```
pin ──R1──┬──R2──┬──C3──┬──R4──┬───► a la entrada del amplificador
          C1     C2     R3     R5
          │      │      │      │
         GND    GND    GND    GND
```

La salida va a la entrada de un amplificador de instrumento o a una entrada de línea. Para auriculares hace falta un amplificador de auriculares, nunca el pin.

## La pista de la microSD

El pedal no tiene entrada de audio hasta la Fase 11, así que la fuente es una grabación de la tarjeta. El formato son bloques crudos, como el banco de programas: cabecera con magia, número de muestras y CRC-32, y después muestras de 16 bit con signo (256 por bloque).

```
sofifi pista build/pista.img guitarra.wav                 toda la grabación
sofifi pista build/pista.img guitarra.wav --segundos 20   solo 20 s
sofifi pista --leer build/pista.img                       comprueba la cabecera
```

La imagen se escribe en la tarjeta como el banco de programas (`docs/microsd.md`, paso 4).

- La salida de 1 bit es mono: dos canales se promedian.
- El WAV se remuestrea a 48 828,125 Hz si viene a otra frecuencia.
- La pista se repite sin parar: al acabar, el lector vuelve al primer bloque.
- **La pista tiene un mínimo de 256 muestras** (5,2 ms). Con menos, cada vuelta
  vuelve a leer un bloque entero para pocas muestras y la cola del lector se
  queda sin datos.

Una tarjeta lenta también puede vaciar la cola. El lector lo dice con su señal `vacio`, y el top de la placa lo informará por la UART (PR 3). La cola aguanta 21 ms y un bloque tarda unos 0,33 ms.

## El pin

> **Advertencia.** Antes de conectar nada, comprueba el pin contra el esquema de tu Dock.

El audio sale por el pin **G8** del conector **J6**, el del PMOD TF. Con la revisión v2 del módulo, ese pin es DAT2 de la tarjeta y el modo SPI no lo usa. La bola está verificada para J6 [V]; el uso como salida de audio es una decisión de conveniencia, no un dato del esquema.

Cuando tengas el esquema del Dock delante, conviene mover el audio a un pin libre de J4 o J5. Solo hay que cambiar una línea de `rtl/top/primer25k.cst`.

Con un módulo PMOD TF de la revisión v1 no funciona, y se nota: G8 es su SCK. El estado de la UART lo dice con `sd_error` y el código 1 (CMD0).

## Cómo se oye un programa

1. Escribe la pista en la imagen: `sofifi pista build/pista.img --sintetica`.
2. Copia la imagen a la tarjeta, como el banco de programas (`docs/microsd.md`).
3. Monta el filtro RC y conecta su salida a la entrada de un amplificador.
4. Carga el top con el programa que quieras oír: `make audio AUDIO=plate`.
   Sin `AUDIO`, suena el plate.
5. Lee el estado por la UART: `make uart`.

Cada 4 096 muestras (unas 12 veces por segundo) la placa envía una línea
`E <estado><dac_l>`, de 12 dígitos hexadecimales. El estado lleva, de bit alto
a bajo:

| Bits | Qué dice |
|---|---|
| 23 a 13 | cero |
| 12 | `sd_listo`: la tarjeta arrancó |
| 11 | `listo`: la cabecera de la pista es válida |
| 10 | `preparado`: ya hay audio y el núcleo corre |
| 9 | `vacio`: la cola se quedó sin datos alguna vez |
| 8 | `error` de la pista |
| 7 a 5 | motivo: 1 tarjeta, 2 magia, 3 versión, 4 CRC, 5 número de muestras |
| 4 | `sd_error` |
| 3 a 0 | código de `sd_spi`: 1 CMD0, 2 CMD8, 3 ACMD41, 4 CMD58, 5 CMD17, 6 token |

Un estado de `0C00` con los últimos dígitos a cero quiere decir que todo va
bien: tarjeta lista, cabecera válida y audio corriendo.

La cadena se comprueba también en simulación, sin placa:
`pytest sim/salida sim/sd sim/top/audio_sd_test.py`.

## Recursos en el chip

| Recurso | Uso de `audio_sd` |
|---|---|
| LUT4 | 12 593 de 23 040 (55 %) |
| Flip-flops | 7 646 de 23 040 |
| ALU | 1 566 de 17 280 |
| BSRAM | 49 de 56: 42 de retardo, 6 de microcódigo y 1 de la cola de la pista |
| DSP | 2 de 28 |
| Reloj | 107 MHz en nextpnr; el margen real se mide en la placa (ADR 0011) |

## Qué puede ir mal

| Síntoma | Causa probable |
|---|---|
| Un silbido agudo y fuerte | falta el filtro RC, o un condensador está mal soldado |
| Un zumbido grave | la masa de la placa y la del amplificador no están unidas |
| Suena muy bajo | el divisor atenúa demasiado para esa entrada; subir R5 |
| Suena recortado | la pista está grabada muy caliente; el recorte de ±13/16 actúa (ADR 0015) |
