# Mapeo de cumplimiento

> **Qué no es esto:** un mapeo de controles, no una auditoría. No lo ha revisado un tercero, no hay pentest, y quien lo escribió es quien escribe el código que evalúa. Estado a 2026-10-09 (versión 0.7, sin producto todavía; la Fase 08 está en curso).

## Huecos primero

| Hueco | Riesgo | Toca |
|---|---|---|
| Presets de texto de la microSD sin parser todavía | Un fichero malformado podría cargar mandos fuera de rango | CWE-20, CWE-787, CWE-125 |
| Banco de microcódigo validado solo en simulación | El cargador comprueba límites y CRC-32 (`rtl/sd/cargador.v`), pero no se ha probado con una tarjeta real (Fase 08) | CWE-20, CWE-787, A08 |
| Entrada MIDI sin parser endurecido | Mensajes SysEx largos que desborden el buffer | CWE-20, CWE-120 |
| Microcódigo con CRC-32 pero sin firma | El CRC detecta daños, no a un atacante con la tarjeta: un programa con CRC correcto se carga. Solo puede dar audio raro, porque toda dirección cae dentro de su memoria de retardo | A08, CWE-345 |
| Volumen de salida sin limitador de seguridad | Freeze o feedback descontrolado que dañe el oído o el equipo | Seguridad física (fuera de OWASP) |

## OWASP Top 10 (2021)

| Categoría | Estado | Control / motivo |
|---|---|---|
| A01 Control de acceso | No aplica | Dispositivo standalone sin usuarios ni red |
| A02 Criptografía | No aplica | No hay secretos en el producto. La higiene de secretos del repositorio la cubre `scripts/check_secrets_hygiene.sh` |
| A03 Inyección | Parcial | El banco de microcódigo no tiene sistema de ficheros ni punteros: la ranura sale del índice (`model/sofifi/domain/banco.py`). Faltan los parsers de presets y MIDI |
| A04 Diseño inseguro | Parcial | Decisiones con ADR (`docs/adr/README.md`); falta el limitador de salida |
| A05 Configuración | No aplica | Sin servicios expuestos |
| A06 Componentes vulnerables | Parcial | Licencias y origen en `docs/terceros.yaml` + `scripts/check_licenses.py`; sin auditoría de CVEs de las herramientas de desarrollo |
| A07 Autenticación | No aplica | Sin usuarios |
| A08 Integridad | Parcial | El microcódigo lleva CRC-32 y se valida antes de cargar; el microcódigo y el bitstream no llevan firma |
| A09 Registro | No aplica | Sin servicio |
| A10 SSRF | No aplica | Sin red |

## OWASP API Security Top 10

No aplica: el producto no expone ninguna API de red. Se reevalúa si se añade USB-MIDI o control remoto.

## CWE Top 40

Aplican las relativas a memoria y parsing en el RTL: CWE-787, CWE-125, CWE-20, CWE-120 y CWE-190. El pedal no tiene CPU ni firmware.

| CWE | Estado |
|---|---|
| CWE-190 (desbordamiento entero) | mitigado por diseño en la aritmética DSP: saturación explícita (ADR 0003) |
| CWE-20, CWE-787, CWE-125 (validación y límites) | el cargador de la microSD comprueba cada campo antes de escribir (Fase 08, en simulación) |
| CWE-120 (copia sin límite) | pendiente hasta el parser de MIDI |

## NIST AI RMF

No aplica al producto: no hay ningún modelo de IA en el pedal. En el **desarrollo** se usan agentes: el contenido externo que traen (papers, foros, fichas) es dato citado, no instrucción (SPEC_RAIZ P10), y las cifras llevan marca de confianza en `docs/investigacion/INVESTIGACION.md`.
