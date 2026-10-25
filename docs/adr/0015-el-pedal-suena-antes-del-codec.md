# ADR 0015 — El pedal suena antes del códec: una salida de 1 bit

- **Estado:** Aceptado · 2026-10-24
- **Revisión prevista:** cuando llegue el códec I2S (Fase 11). La salida de 1 bit no se retira: queda como salida de depuración y de demostración.

## Contexto

El catálogo tiene 86 programas y 1 032 presets. Ninguno se ha oído en la placa. Las demos se generan con el modelo en el PC (`scripts/generar_demos.py`). En la placa, el núcleo solo demuestra que da los mismos bits que el modelo, por la UART (ADR 0003, MED-13 y MED-17).

Las fases 09, 10 y 11 esperan hardware que no está comprado: el códec I2S, el MCP3208 y la OLED. Mientras tanto, el criterio «suena con guitarra» de `docs/investigacion/ESTADO_DEL_ARTE_2026.md` sigue en «no».

Las pruebas acústicas de la Fase 06 encontraron cuatro fallos de programación que ninguna huella vio (fails.md, F-18). Oír es una prueba, no un adorno.

La FPGA tiene un recurso que no se usa: el reloj de 100 MHz es 2 048 veces fs (ADR 0005). Con ese factor de sobremuestreo, un solo pin de salida basta para llevar audio.

## Opciones evaluadas

1. **Esperar el códec I2S** (Fase 11). No cuesta ni una LUT. Deja el proyecto sin audio hasta que llegue una compra.
2. **Salida de 1 bit con conformado de ruido**, en un pin de un PMOD, con un filtro RC pasivo de dos polos. El hardware son dos resistencias y dos condensadores.
3. **PWM de N bit.** Es más simple, pero el ruido queda en banda: con 12 bit de resolución, la frecuencia de la PWM baja a 24,4 kHz.
4. **DAC R-2R de 8 bit** en ocho pines del Dock. Más cableado, 8 pines y el ruido de conmutación de ocho salidas a la vez.

## Decisión

Opción 2, con la cadena de interpolación de Hogenauer (Meyer-Baese, *DSP with FPGAs*, §5.3) y un modulador de segundo orden con realimentación distribuida.

```
muestra S.23 a fs ─► recorte ±13/16 ─► CIC S=2, R=32 ─► mantenimiento ×64 ─► modulador Σ∆ ─► 1 bit a 100 MHz
                                          32·fs                100 MHz             2.º orden
```

- **Interpolador CIC:** dos peines a fs y dos integradores a 32·fs. Sin multiplicadores. Acumuladores de 32 bit en aritmética modular, y la salida se trunca a S.23. La ganancia del interpolador es `R^(S-1) = 32`, no `R^S`: el relleno de ceros divide por `R`.
- **Mantenimiento ×64:** el modulador repite la muestra 64 ciclos. Las imágenes del mantenimiento quedan en 1,5625 MHz, donde el filtro RC las atenúa.
- **Modulador:** segundo orden, coeficientes `k1 = 1` y `k2 = 4`, que son desplazamientos y no productos. Integradores de 28 bit con saturación. Sin dither: no hace falta (sección «Medidas»).
- **Recorte de seguridad a ±13/16 de escala plena, antes del modulador.** Es un requisito de seguridad, no de calidad (SECURITY.md). Un programa de la microSD puede saturar a ±1. Con la entrada a escala plena, el segundo integrador satura y el modulador sale de su zona lineal.
- **Un solo dominio de reloj.** El modulador corre a 100 MHz, el mismo reloj del núcleo (ADR 0005). No hay cruce de dominio.
- **El modelo manda** (ADR 0003): `model/sofifi/domain/salida_1bit.py` es el oráculo, y el testbench compara el flujo de bits uno a uno.
- **Qué NO es:** no es la salida del pedal. El pedal final usa el códec I2S de la Fase 11 y el limitador de la Fase 12. Esta salida es para oír, medir y demostrar.

## Medidas en el modelo

Tono de 953 Hz, ventana en régimen permanente de 256 muestras, relación señal/ruido en la banda de 0 a 20 kHz [V]:

| Entrada | SNR en banda | Ruido en banda |
|---|---|---|
| −2 dBFS | 117 dB | −122 dBFS |
| −6 dBFS | 113 dB | −122 dBFS |
| −12 dBFS | 107 dB | −122 dBFS |
| −20 dBFS | 62 dB | −85 dBFS |
| −26 dBFS | 93 dB | −122 dBFS |

- El ruido en banda queda en −122 dBFS, salvo en amplitudes concretas. A −20 dBFS sube a −85 dBFS: es un ciclo límite del modulador en esa amplitud [V]. Sigue muy por debajo de lo que dan un pin LVCMOS de 3,3 V y un filtro RC [INF].
- **Con `k2 = 2` la caída es peor y más ancha:** 68 dB a −14 dBFS. Por eso `k2 = 4`.
- **Dither:** no sirve. Para cambiar la decisión del cuantificador de 1 bit, el dither tiene que ser una fracción apreciable de la escala plena, y entonces él mismo es el ruido. Con 14 bit de dither, las cifras no cambian ni en una décima de dB [V].
- **Reposo limpio:** con la entrada a cero, la salida alterna y no hay tono de reposo en banda.
- **Estabilidad:** con el recorte, ningún caso satura los integradores. Peor excursión medida: 4,42 veces la escala plena en el primer integrador y 7,32 en el segundo, de 16 que admiten los 28 bit. Casos probados: seno, onda cuadrada, ruido y DC, todos a escala plena.
- **Caída en banda del interpolador:** la interpolación lineal atenúa −0,44 dB a 6 kHz y −5,1 dB a 20 kHz [INF]. Para una guitarra, cuyo contenido acaba hacia 6 kHz, es despreciable. Se declara y no se compensa.

## Consecuencias

- Los 86 programas se pueden oír en la placa. La fuente de audio es la microSD (Fase 13, PR 2), porque el pedal no tiene entrada analógica hasta la Fase 11.
- Carpeta nueva `rtl/salida/`, con tres módulos: `cic_interp.v`, `sigma_delta.v` y `salida_1bit.v`.
- Un pin nuevo en `rtl/top/primer25k.cst`, que es sentinela. Por eso este ADR.
- La salida de 1 bit **no sustituye** al limitador de la Fase 12. El recorte a 13/16 acota la amplitud, no la energía de un feedback.
- Coste en la placa, medido en la segunda vuelta de la fase. Estimación: 300 a 600 LUT4 y 0 DSP [INF].
- El filtro RC y el jack entran en `BOM.md` como componentes de laboratorio, no del pedal final.

## Alternativas descartadas

- **PWM:** el ruido de cuantificación no se aparta de la banda de audio.
- **R-2R:** ocupa 8 pines y añade ruido de conmutación; la precisión depende de las resistencias.
- **Entrada de audio por sigma-delta** (comparador o par LVDS con realimentación RC): no entra en esta fase. Haría al pedal tocable con dos resistencias más, pero no está confirmado que los bancos del GW5A lo permitan en los pines del Dock [?]. Se estudiará con su propio ADR.
