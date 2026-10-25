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

## Cómo se oye un programa

El pin y el top llegan en el PR 3 de la Fase 13. Los pasos serán estos:

1. Escribir una pista de audio en la microSD con `sofifi pista`.
2. Cargar el top de audio: `make prog TOP=audio_sd`.
3. Elegir el programa y escuchar.

Mientras tanto, la cadena se comprueba en simulación: `pytest sim/salida`.

## Qué puede ir mal

| Síntoma | Causa probable |
|---|---|
| Un silbido agudo y fuerte | falta el filtro RC, o un condensador está mal soldado |
| Un zumbido grave | la masa de la placa y la del amplificador no están unidas |
| Suena muy bajo | el divisor atenúa demasiado para esa entrada; subir R5 |
| Suena recortado | la pista está grabada muy caliente; el recorte de ±13/16 actúa (ADR 0015) |
