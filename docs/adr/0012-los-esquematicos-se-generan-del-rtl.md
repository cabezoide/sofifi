# ADR 0012 — Los esquemáticos se generan del RTL, no se dibujan

- **Estado:** Aceptado · 2026-10-07
- **Revisión prevista:** si netlistsvg deja de mantenerse, o si un módulo crece tanto que su esquemático deja de servir.

## Contexto

La persona propietaria pide un esquemático en notación electrónica por cada módulo RTL, en PNG o PDF. Un esquemático dibujado a mano se queda viejo en cuanto cambia el Verilog, y nadie lo nota. El proyecto ya aplica esa regla a lo generado: tablas del RTL, catálogo de programas y demos.

## Opciones evaluadas

1. Dibujar a mano (KiCad, draw.io).
2. `yosys show` (Graphviz): cajas y flechas, no símbolos electrónicos.
3. Yosys → JSON → **netlistsvg**: símbolos estándar (multiplexores, sumadores, comparadores, flip-flops, puertas) y colocación automática.

## Decisión

Opción 3.

- `scripts/esquematicos.py` elabora cada módulo de `rtl/` con Yosys (`proc; opt; clean`, sin aplanar) y lo dibuja con netlistsvg.
- La salida es **PDF vectorial** en `schematics/<carpeta>/<módulo>.pdf`, con un cajetín: módulo, descripción, fuente y sha256 de la fuente. Las páginas de más de 14 000 puntos se escalan; el dibujo no pierde detalle.
- `schematics/README.md` es el índice y guarda el sha de cada fuente.
- **Licencias:** netlistsvg es MIT; su motor de colocación, elkjs, es EPL-1.0. Se usan como herramientas, en `herramientas/esquematicos/` con `package-lock.json`; `node_modules` no se versiona. No se copia su código (ADR 0002).
- **Compuerta blanda `esquematicos`:** `--comprobar` compara los sha. Es blanda porque necesita Node y chrome-headless-shell, que no todo el mundo tiene (P1).

## Consecuencias

- Un cambio de RTL pide regenerar: `make esquematicos`. La compuerta blanda lo recuerda.
- Los módulos grandes (`nucleo`, `tabla_hermite`) dan dibujos enormes. Sirven para buscar una señal; la vista de conjunto está en `docs/arquitectura_fpga.md`.
