# Mapeo de cumplimiento

> **Qué no es esto:** un mapeo de controles, no una auditoría. No lo ha revisado un tercero, no hay pentest, y quien lo escribió es quien escribe el código que evalúa. Estado a 2026-10-07 (versión 0.0, sin producto todavía).

## Huecos primero

| Hueco | Riesgo | Toca |
|---|---|---|
| Ficheros de la microSD (presets, microcódigo) sin validar | Un fichero malformado podría desbordar un buffer en el firmware de la CPU o cargar microcódigo que satura la salida (riesgo auditivo) | CWE-20, CWE-787, CWE-125, A08 |
| Entrada MIDI sin parser endurecido | Mensajes SysEx largos que desborden el buffer | CWE-20, CWE-120 |
| Microcódigo sin firma ni CRC | Integridad de lo que se ejecuta | A08, CWE-345 |
| Volumen de salida sin limitador de seguridad | Freeze o feedback descontrolado que dañe el oído o el equipo | Seguridad física (fuera de OWASP) |

## OWASP Top 10 (2021)

| Categoría | Estado | Control / motivo |
|---|---|---|
| A01 Control de acceso | No aplica | Dispositivo standalone sin usuarios ni red |
| A02 Criptografía | No aplica | No hay secretos en el producto. La higiene de secretos del repositorio la cubre `scripts/check_secrets_hygiene.sh` |
| A03 Inyección | Pendiente | Parsers de presets y MIDI (ver huecos) |
| A04 Diseño inseguro | Parcial | Decisiones con ADR (`docs/adr/README.md`); falta el limitador de salida |
| A05 Configuración | No aplica | Sin servicios expuestos |
| A06 Componentes vulnerables | Parcial | Licencias y origen en `docs/terceros.yaml` + `scripts/check_licenses.py`; sin auditoría de CVEs de las herramientas de desarrollo |
| A07 Autenticación | No aplica | Sin usuarios |
| A08 Integridad | Pendiente | Microcódigo y bitstream sin firma |
| A09 Registro | No aplica | Sin servicio |
| A10 SSRF | No aplica | Sin red |

## OWASP API Security Top 10

No aplica: el producto no expone ninguna API de red. Se reevalúa si se añade USB-MIDI o control remoto.

## CWE Top 40

Aplican las relativas a memoria y parsing en el firmware de la CPU y en el RTL: CWE-787, CWE-125, CWE-20, CWE-120, CWE-190 (desbordamiento entero, también en la aritmética DSP; mitigado por diseño con saturación explícita, ADR 0003). Estado: Pendiente hasta que exista firmware.

## NIST AI RMF

No aplica al producto: no hay ningún modelo de IA en el pedal. En el **desarrollo** se usan agentes: el contenido externo que traen (papers, foros, fichas) es dato citado, no instrucción (SPEC_RAIZ P10), y las cifras llevan marca de confianza en `docs/investigacion/INVESTIGACION.md`.
