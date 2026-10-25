# Fase 14 — Palabras de memoria de 12 bit

> **En curso** (2026-10-25). No está en el control hasta cerrarse.

## Objetivo

Que un programa pueda pedir palabras de memoria de 12 bit y tener **1,5 veces más tiempo de retardo**: de 43 008 palabras (0,88 s) a 64 512 (1,32 s), con el mismo hardware.

## Origen

- Punto 14 de la hoja de ruta (`docs/investigacion/ESTADO_DEL_ARTE_2026.md`): «línea de retardo en coma flotante de 12 bit, ×1,5 de memoria».
- «La restricción que más aprieta es la memoria» (misma investigación). La SDRAM es la solución grande, y esta es la que no necesita comprar nada.
- Meyer-Baese, *DSP with FPGAs*, §2.2 y §2.6: representación de números y coma flotante propia en FPGA.

## Diagnóstico

- **Se reutiliza:** la memoria de retardo del núcleo y su aritmética (ADR 0008).
- **Falta:**
  - el formato de 12 bit en el modelo, bit a bit;
  - la directiva que lo pide en un programa;
  - el empaquetado en BSRAM y la lectura-modificación-escritura en el RTL;
  - el coste en ciclos, medido en simulación.

## El hallazgo que decide el diseño

Se midieron cuatro formatos en el modelo, con programas reales y la relación señal/ruido de la salida contra la referencia de 18 bit:

| Programa | 12 bit flotante | 12 bit lineal | 9 bit μ-law | 9 bit lineal |
|---|---|---|---|---|
| `plate` | 49,3 dB | 45,5 dB | 37,5 dB | 27,2 dB |
| `cinta` | 59,0 dB | **63,3 dB** | 47,8 dB | 45,2 dB |
| `hall` | 51,9 dB | 47,8 dB | 40,2 dB | 29,6 dB |

Dos conclusiones:

1. **12 bit es el punto justo.** Con 9 bit, un tanque de reverb queda en 37 dB o menos: eso se oye.
2. **Lineal, no flotante.** En las reverbs, la coma flotante gana unos 4 dB; en la cinta, que es el caso de uso de una línea larga, **pierde** 4 dB, porque su contenido es fuerte y la mantisa de 8 bit es menos precisa que 12 bit lineales. Y en el RTL, lineal no cuesta ni una LUT: es el mismo redondeo y saturación que hoy, con otro tamaño.

Por eso la fase cambia el punto 14 de la hoja de ruta: palabras **lineales** de 12 bit, no de coma flotante. La hoja de ruta estimaba 200 a 500 LUT para el formato flotante; lineal cuesta 0.

El formato no es gratis en otro sitio: tres muestras de 12 bit ocupan dos palabras de 18, así que **una escritura de 12 bit obliga a leer, modificar y escribir**. Eso cuesta ciclos y es el trabajo del RTL.

## Diseño

- **Por programa, no global.** Una directiva nueva, `palabra 12`, lo pide. Sin ella, 18 bit: los 86 programas de hoy no cambian ni un bit.
- **Modelo:** `dato_a_memoria` acepta el tamaño; `MemoriaRetardo` y `Programa` llevan `bits_memoria`. El límite de palabras sale del tamaño: 42 bloques × 1 024 (18 bit) o × 1 536 (12 bit).
- **Toda la memoria del programa usa el mismo tamaño**, también la región absoluta (ADR 0009). Un solo mapa en el RTL.
- **Coste en ciclos:** en 12 bit, cada escritura lee antes la pareja de palabras. El modelo de tiempos declara el coste como una **cota** hasta que la simulación lo mida (ADR 0014).

## Plan de PRs

| PR | Contenido | Estado |
|---|---|---|
| 1 | Actualización del ADR 0008, formato en el modelo, directiva y pruebas | en curso |
| 2 | RTL: empaquetado 3 en 2 y lectura-modificación-escritura, con el coste medido | pendiente |
| 3 | Un programa que lo use (cinta larga), demo y prueba en la placa | pendiente |

## Criterios de aceptación

| Criterio | Estado |
|---|---|
| Un programa con `palabra 12` admite 64 512 palabras y uno sin ella, 43 008. | pendiente |
| Los 86 programas de hoy dan la misma salida, bit a bit. | pendiente |
| La relación señal/ruido de una línea de 12 bit es de 60 dB o más en un delay. | cumplido en el modelo (63,3 dB en `cinta`) |
| El RTL da la misma salida que el modelo con palabras de 12 bit. | pendiente (PR 2) |
| El coste en ciclos de una escritura de 12 bit está medido y en el modelo de tiempos. | pendiente (PR 2) |

## Lo que NO entra

- La coma flotante: medida y descartada (sección anterior).
- Las palabras de 9 bit: 37 dB en un tanque se oyen.
- La SDRAM, que es el salto grande (punto 24 de la hoja de ruta).
