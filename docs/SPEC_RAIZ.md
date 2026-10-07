# SPEC-RAÍZ — lo que se lleva uno de OM a cualquier proyecto nuevo

> **Qué es esto.** La destilación de lo que funcionó en **SandyClaw_OM** a lo largo
> de 248 fases, 87 ADRs, 356 ficheros de prueba y 24 trabajos de compuerta, escrita
> de forma que **no dependa de OM**: aquí no hay nodos, ni DAG, ni MSSP. Hay
> disciplina de flujo, disciplina de documentación, disciplina de pruebas,
> arquitectura hexagonal en los dos lados, SOLID con mecanismo concreto, y el
> aparato de seguridad (OWASP · OWASP API · CWE Top 40 · NIST AI RMF) con
> evidencia trazable.
>
> **Qué NO es.** No es una metodología para convencer a nadie, ni un manifiesto.
> Cada regla de aquí existe porque **algo se rompió sin ella** y está anotado el
> fallo que la motivó. Una regla sin ese fallo delante es una preferencia, y las
> preferencias no se blindan con compuertas.
>
> **Cómo se usa.** Se copia en el repositorio nuevo como `docs/SPEC_RAIZ.md` y se
> ejecuta el §11 (*Kit de arranque*) el día 0. Lo demás se adopta por olas: una
> disciplina que entra entera el primer día se abandona el segundo.
>
> Origen: repositorio OM, estado 2026-09-21. Las cifras citadas son las medidas
> allí, y están para dar **orden de magnitud del coste**, no para copiarse.

---

## Índice

| § | Bloque | Qué resuelve |
|---|---|---|
| 1 | [Principios rectores](#1-principios-rectores) | Las quince frases de las que se derivan las demás reglas |
| 2 | [Disciplina de flujo](#2-disciplina-de-flujo) | Rama, compuerta, PR, orden de entrega, fases |
| 3 | [Disciplina de documentación](#3-disciplina-de-documentación) | ADR, mapas para agentes, registros canónicos, docs generadas |
| 4 | [Disciplina de pruebas](#4-disciplina-de-pruebas) | Las once clases de prueba y cuál es compuerta |
| 5 | [Arquitectura del backend (hexagonal)](#5-arquitectura-del-backend-hexagonal) | Capas, puertos, ciclos, descomposición |
| 6 | [Arquitectura del frontend (por capas)](#6-arquitectura-del-frontend-por-capas) | La frontera única y cómo se blinda |
| 7 | [SOLID con mecanismo](#7-solid-con-mecanismo) | Cada letra con su verificador |
| 8 | [Seguridad: OWASP, OWASP API, CWE Top 40](#8-seguridad-owasp-owasp-api-cwe-top-40) | Controles, mapeo con evidencia y sus compuertas |
| 9 | [Calidad medible](#9-calidad-medible-ratchets-madurez-mediciones-promesas) | Ratchets, madurez, mediciones, promesas |
| 10 | [Catálogo de compuertas](#10-catálogo-de-compuertas) | La tabla completa: duro, blando, de release |
| 11 | [Kit de arranque](#11-kit-de-arranque-el-día-0) | Qué ficheros existen antes de la primera línea de producto |
| 12 | [Antipatrones y su cura](#12-antipatrones-observados-y-su-cura) | Los doce fallos que se repiten |
| 13 | [Listas de comprobación](#13-listas-de-comprobación) | PR, fase cerrada, módulo nuevo |

---

## 1. Principios rectores

Quince frases. Todo lo demás en este documento es una consecuencia de alguna.

**P1 — Un gate que bloquea lo inarreglable se desactiva, y entonces deja de
proteger de lo que sí.**
Una compuerta solo puede exigir lo que quien la cruza puede arreglar hoy. El
filo correcto no es «severidad», es «severidad **y** arreglo disponible»; no es
«cero violaciones», es «ni una más que ayer». Si una compuerta necesita un
navegador, un clúster o una herramienta que no todo el mundo tiene, no es
condición de *push*: es compuerta de *release*.

**P2 — Una promesa sin verificador es una promesa no verificada, y se dice.**
No bloquea *no haber comprobado*; bloquea **declarar comprobado lo que nadie
comprobó**. Un `no_verificada` con su motivo es un estado legítimo y se publica.

**P3 — Todo verde declara su alcance y lo que no cubre.**
`scope` y `no_cubre` son obligatorios en cualquier registro de evidencia. Un
verde sin frontera declarada se lee como «todo está bien», que casi nunca es lo
que el verde significa.

**P4 — Las magnitudes también se blindan, con el mismo mecanismo que las
propiedades booleanas.**
Acoplamiento, cobertura, tamaño de fichero, tipado, pasos de un recorrido,
violaciones de accesibilidad: un número en un fichero versionado que **alguien
tiene que mover a mano**, con el motivo escrito. No exige mejorar; exige **no
empeorar en silencio**. La fuga lenta es el enemigo: ninguna entrega empeora de
forma llamativa, todas empeoran un poco.

**P5 — Una medición caduca, y al caducar la nota baja sola.**
Un número sin fecha, umbral, entorno y caducidad no es una medición: es una cifra
de portada. Al vencer, la compuerta se pone roja **por el paso del tiempo**, aunque
nadie haya tocado nada, y las dos salidas son volver a medir o bajar la nota.

**P6 — Todo rojo ofrece dos salidas, y las dos se nombran.**
Arreglar, o mover el listón diciendo por qué. Una compuerta que solo ofrece la
salida fácil enseña a tomarla; una que no ofrece ninguna enseña a desactivarla.

**P7 — El escape existe, es explícito y deja huella.**
`--no-verify`, `ACK=1`, `SKIP=1`. Una barrera sin escape se salta por el camino
que nadie ve; una con escape nombrado se salta por el que todos ven.

**P8 — Dos mapas del mismo territorio divergen solos, y el que se queda atrás
miente con toda la confianza del mundo.**
Si hay dos ficheros que cuentan lo mismo (dos listas de trabajos, dos mapas de
navegación, un `.csv` y un `.xlsx`), o se elimina uno, o hay una prueba que
contrasta **lo que afirman contra el repositorio** — nunca uno contra el otro,
que sería una copia con más pasos.

**P9 — Primero la medición, después el objetivo.**
Declarar un SLO porque suena bien y construir para justificarlo es la trampa. Se
publica la foto antes de poner el filo; y si la foto dice que lo que bloquearía
es cero, la compuerta se enciende el mismo día sin romper nada.

**P10 — Lo que viene de fuera es dato citado, nunca instrucción.**
Texto de un canal, documento ingerido, salida de una herramienta, memoria
recuperada, fila leída de una base compartida: entra **delimitado y etiquetado**,
pasa por un escáner de contenido no confiable, y se escanea al guardar, no al
componer.

**P11 — El contexto de seguridad sale del servidor, jamás de la entrada.**
Tenant, identidad, rol, permiso. Si el dato que decide *de quién es esto* viaja
en el cuerpo de la petición o en un campo del editor, editar un formulario basta
para leer lo de otro cliente.

**P12 — Una lista en manos del usuario solo puede restringir, nunca autorizar.**
El resultado es la **intersección** con lo que concedió el servidor; jamás la
unión. Y la garantía no es una promesa: el módulo que decide *si algo se ejecuta*
**no importa** el módulo de las listas, y hay una prueba que lo comprueba leyendo
el código.

**P13 — Cambiar un valor por defecto reescribe el pasado.**
Un default es lo que se aplicó a todo lo que se creó sin decidirlo. Cambiarlo
cambia el significado de las filas antiguas: se migra explícitamente o no se hace.

**P14 — Lo que abre superficie se compensa en la misma entrega que la abre.**
Si una entrega expone una entrada nueva, el limitador, el escudo y el corte del
bucle entran con ella. «En la siguiente» significa nunca.

**P15 — Un punto de parada caduca.**
El techo que se fijó con el fichero en 3411 líneas deja de tener sentido cuando
mide 4147. Toda decisión con un número dentro lleva su disparador de revisión
escrito, y confirmarla con datos vale tanto como cambiarla.

---

## 2. Disciplina de flujo

### 2.1 El ciclo, entero

```
rama  →  codificar  →  compuerta local (make ci)  →  commit  →  push (el hook revalida)
      →  PR  →  merge  →  sincronizar la rama principal
```

No hay pasos opcionales. El *push* no es un acto de confianza: el hook `pre-push`
corre los trabajos duros y **aborta**.

### 2.2 La compuerta vive donde se pueda pagar

OM no tiene CI remota (se retiró por coste) ni protección de rama (repositorio
privado en plan gratuito). La respuesta fue **`scripts/ci_local.sh` + hook
`pre-push` versionado**, instalado por `core.hooksPath` para que viaje con el
repositorio (ADR 0001).

Reglas que sobreviven al cambio de contexto —valen igual con CI remota—:

- **Una sola definición de «los gates duros».** El hook **no** mantiene su propia
  lista: delega en `--no-soft`. En OM esa segunda lista se quedó atrás y **cinco
  compuertas duras dejaron de bloquear ningún push** durante meses, sin que fuera
  una decisión de nadie (P8).
- **Trabajos seleccionables.** `ci_local.sh backend frontend` para iterar;
  el ciclo corto no paga el peaje del ciclo largo.
- **La compuerta se cronometra a sí misma** y escribe su tiempo en un fichero
  local no versionado. Un número de experiencia de desarrollo envejece más rápido
  que ninguno; con coste cero, se mide siempre.
- **Coste declarado.** En OM: 180 s en el caso común (cambio de lógica), 381 s en
  frío, 82 s de instalación limpia. El coste de la barrera es parte de la
  decisión, y por eso se revisa con los dos costes delante, no con uno.
- **Los trabajos caros pero valiosos son compuerta de *release*, no de *push***
  (P1): carga con `k6`, accesibilidad sobre la aplicación levantada, recorridos
  con navegador, auditoría de postura.

### 2.3 Tres clases de compuerta, y la clase se declara

| Clase | Qué significa | Consecuencia de un rojo |
|---|---|---|
| **Dura** | Todo el mundo puede correrla y arreglarla hoy | El *push* se aborta |
| **Blanda** | Exige herramienta externa, o es informativa | Sale `WARN`, no bloquea |
| **De release** | Cara, pero condición para promover a producción | No se promueve |

Una compuerta blanda **no es una compuerta rota**: es una que declara que su
rojo no puede ser condición de *push*. Lo que no se hace jamás es fingir que se
ejecutó: si no corre, el informe publica el hueco.

### 2.4 El escape consciente

Tres, todos con nombre y todos ruidosos: `git push --no-verify` (git ni ejecuta
el hook), `PREPUSH_SKIP=1` (el hook lo dice y sigue), `ADR_GATE_ACK=1` (revisé y
ninguna decisión cambia). Se usan en emergencias y se ven en el historial de la
terminal. La alternativa —una barrera sin escape— produce ramas que nunca se
empujan y compuertas comentadas (P7).

### 2.5 El trabajo se organiza en fases, y la fase tiene spec

- **Una fase = una spec versionada** en `docs/fases/`, con secciones fijas:
  **Objetivo · Origen · Diagnóstico (lo que ya existe y se reutiliza / lo que
  falta) · El hallazgo que decide el diseño · Diseño · Plan de PRs · Criterios de
  aceptación · Lo que NO entra**.
- **El «hallazgo que decide el diseño» es obligatorio.** Es la frase que explica
  por qué la solución obvia no sirve. Una spec sin hallazgo es una lista de
  tareas, y una lista de tareas no sobrevive al primer imprevisto.
- **El título es técnico, nunca evocativo**, y vive en cuatro sitios que no pueden
  divergir: el H1 de la spec, la columna `titulo` del control, la sección del
  consolidado y el ADR que cita. Lo comprueba una compuerta (P8).
- **Una fase planificada no entra en el control.** El control se cierra al cerrar
  la fase, no al planificarla: un registro que declara futuro deja de decir qué
  hay.
- **Al cerrar, la descripción del control cuenta el hallazgo y las enmiendas** —qué
  se cambió respecto de la spec al implementar y por qué—. Es el único sitio donde
  queda escrito que la spec se equivocaba en algo concreto.
- **La versión del producto es la última fase cerrada** (`0.<fase>`). Simple,
  derivable y sin ceremonia.

### 2.6 Entrega en pila de PRs

Una fase se parte en **4-6 PRs encadenados**, cada uno con la compuerta en verde
por separado. El orden que funcionó: *(0)* medición o foto previa si la fase toca
una decisión con número dentro (P9); *(1)* dominio y puertos; *(2)* adaptadores;
*(3)* API/UI; *(4)* documentación, registros y ADR. El PR de documentación **no
es opcional ni se agrupa al final de la fase**: cada PR que toca una decisión
estructural lleva su ADR dentro.

### 2.7 Orden de entrega, sin saltarse pasos

```
local (compuerta verde) → documentación y registros → GitHub (PR + merge) → producción
```

Producción va **después** del merge, nunca antes «para probar»; el despliegue
lleva backup previo obligatorio y no es un *flag*; y la marcha atrás es una
decisión informada, no un botón — el código vuelve solo, pero se **detiene y
nombra las migraciones** cuando el salto atrás las cruza, porque un `downgrade`
puede perder lo escrito desde el despliegue.

---

## 3. Disciplina de documentación

### 3.1 Docs por commit, con compuerta

**Si el cambio toca una decisión estructural, su ADR se actualiza en el mismo
PR.** No es una costumbre: es una compuerta (`adr-gate`) que vigila **sentinelas
curadas** —líneas y ficheros concretos que casi siempre significan que la
decisión cambió, no que se siguió— y bloquea si el diff las toca sin tocar ningún
ADR. Filosofía anti-ruido: sentinelas estrechas, nunca directorios enteros.
Escape: `ADR_GATE_ACK=1`.

### 3.2 ADR: formato fijo, una pantalla

`docs/adr/NNNN-titulo-en-kebab.md`, secciones **Contexto · Opciones evaluadas ·
Decisión · Consecuencias · Alternativas descartadas**, más dos campos que en OM
resultaron ser los más valiosos:

- **Estado y fecha**, y **revisión prevista con su disparador** («solo si cambia
  la situación de coste», «cuando la allowlist quede vacía»). Sin disparador, no
  hay revisión pendiente: se dice.
- **Actualizaciones fechadas al pie.** Un ADR no se reescribe: se le añade
  «Actualización AAAA-MM-DD (qué cambia y por qué)». Reescribirlo borra la
  apuesta que se hizo con la información de entonces (P15).

El **título del ADR es la frase que se recuerda**: «un gate que bloquea lo
inarreglable se desactiva», «el tenant es contexto de ejecución, no entrada del
nodo», «una alerta sin runbook es una interrupción». Un ADR titulado
«Refactor del módulo X» no se cita nunca; uno titulado con su regla se cita solo.

El `README.md` de `docs/adr/` lleva la tabla completa —número, decisión en una
línea, estado—, y es el índice que se lee antes de proponer una mejora.

### 3.3 Mapas de navegación para quien retoma en frío (humano o agente)

Tres ficheros, y una prueba que impide que mientan:

| Fichero | Para quién | Contenido |
|---|---|---|
| `AGENTS.md` (raíz) | cualquier agente; convención [agents.md](https://agents.md) | qué es esto, arranque, dónde vive cada cosa, invariantes, qué no tocar |
| `CLAUDE.md` (raíz) | el agente que lo carga solo | **desarrolla** el anterior: comandos por capa, cómo extender, detalle de ADRs |
| `<subdir>/AGENTS.md` | quien edita esa carpeta | **tiene precedencia**: las reglas de esa capa, sus trampas conocidas |

Reglas que valen:

- El mapa se lee **en menos de cinco minutos** y su promesa es reconstruir el
  modelo mental sin releer el código.
- **Se prueba contra el territorio, no contra el otro mapa** (P8): que los
  comandos citados existan, que las rutas existan, que los ADR citados existan.
- El anidado gana. En OM, durante meses el `AGENTS.md` del frontend solo tenía el
  bloque que genera el framework, así que quien editaba el frontend **no veía ni
  una regla del proyecto**.
- Incluye **«qué no tocar»** y **«trampas conocidas»**: lo que un recién llegado
  rompe sin querer, y lo que parece un fallo del producto y no lo es.

### 3.4 Registro canónico en YAML, documento generado en Markdown

El patrón que más rindió en OM, aplicado cinco veces (promesas, madurez,
mediciones, ratchets, vulnerabilidades aceptadas):

```
docs/<registro>.yaml   ← FUENTE CANÓNICA, diffeable, con el porqué en cada entrada
        │  scripts/build_<registro>.py
        ▼
docs/<REGISTRO>.md     ← GENERADO. No se edita a mano; la compuerta lo detecta
```

- **El `.md` generado se versiona** (para leerlo en el navegador del repositorio)
  y la compuerta comprueba que **coincide con lo que produce el generador**.
  Editarlo a mano es un rojo.
- **Cada entrada lleva su `motivo`** en prosa. Es lo que convierte un número en
  una decisión y no en un residuo. Un listón sin motivo se mueve sin pensar.
- **Los identificadores son estables y no se reutilizan** (`P-001`, `M-14`,
  `MED-08`, `RAT-07`) aunque la entrada se retire.

### 3.5 Documentación derivada de la fuente

Todo lo que se puede derivar, se deriva, y la compuerta comprueba la derivación:

- **Contrato de API**: OpenAPI exportado del código en cada compuerta.
- **Wiki técnica**: Sphinx con `warnings = error` sobre los docstrings reales.
- **Apéndices del manual**: catálogo de capacidades leído del código, de modo que
  una capacidad nueva sin su «para qué» deja un hueco visible.
- **Manual publicado**: si la interfaz enlaza al HTML, el HTML republicado es
  parte de la compuerta. Un capítulo editado y no republicado deja la ayuda
  enseñando la versión anterior **y eso no se ve desde dentro del producto**.
- **Novedades por versión**: el contenido lo escribe una persona (qué gana quien
  *usa* el producto no sale de un control de fases), pero que la versión publicada
  **tenga** su sección lo comprueba la compuerta.
- **Ejemplos ejecutables**: un ejemplo que no se ejecuta no es un ejemplo. Los del
  repositorio se corren en seco, sin red ni coste, en cada compuerta.

Optimización que merece copiarse: **la wiki solo se reconstruye si cambió lo que
lee**. La huella se calcula sobre `docs/` más los **docstrings y firmas** del
código —no el cuerpo de las funciones, que cambia en el 90 % de los commits— y
**del disco, no del último commit**, porque leer del último commit da falso verde
justo cuando se corre la compuerta: con cambios sin *commitear*. Un salto
silencioso es indistinguible de una compuerta rota, así que se dice en pantalla.

### 3.6 Runbooks y alertas, en los dos sentidos

**Una alerta sin runbook es una interrupción; un runbook sin alerta es un
documento que nadie abre.** Hay prueba en ambas direcciones, y una tercera que
comprueba que las alertas consultan **métricas que el producto publica de
verdad** — una alerta sobre una serie inexistente nunca se dispara y da la
sensación de que algo está vigilado. Cinco alertas bien elegidas, no cincuenta.

### 3.7 Deuda cero, literalmente

Un marcador de deuda al **inicio** de un comentario (`TODO`, `FIXME`, `HACK`,
`XXX`) es una compuerta roja. El detalle que lo hace vivible: solo se marca
cuando el comentario **empieza** por el marcador, no cuando la palabra cae en
medio de la prosa. Un marcador es un issue rastreable o no es nada.

---

## 4. Disciplina de pruebas

### 4.1 Convenciones que evitan accidentes

- **Un solo directorio de pruebas y un sufijo propio** (`tests/*_test.py`), con la
  recolección **acotada** en la configuración. En OM el producto guarda scripts
  reales del usuario en disco; sin acotar, el recolector intentaba importar
  *el `test_auth.py` que subió un cliente*.
- **La configuración global de la suite fija el entorno antes del primer import**
  (directorios temporales, motores en memoria, límites). Un adaptador con estado
  en disco y un cliente cacheado en un global **sobreviven de una prueba a la
  siguiente**, y entonces el aislamiento se comprueba contra datos de otra
  prueba: la peor forma de tener un verde.
- **Aislamiento explícito del estado global por proceso** (limitadores, semáforos,
  cachés) con *fixtures* automáticas.
- **Nada se escribe en el árbol de fuentes.** Nunca en el directorio de datos del
  usuario: siempre un temporal.

### 4.2 Las once clases de prueba, y cuál es compuerta

| # | Clase | Qué caza | En OM es |
|---|---|---|---|
| 1 | **Unitarias** | lógica de cada colaborador | dura |
| 2 | **Tests-contrato de arquitectura** | fugas de capa, ciclos, registros incompletos | dura |
| 3 | **Property-based** | invariantes sobre entradas generadas | dura |
| 4 | **Integración con contenedor real** (base de datos) | lo que el motor en memoria miente | dura si hay Docker |
| 5 | **No-drift de migraciones** | modelo cambiado sin revisión | dura |
| 6 | **Ejecución en seco, hermética** | el sistema entero sin red ni coste | dura |
| 7 | **Escenarios end-to-end versionados** | regresiones de **composición** | blanda |
| 8 | **Arnés por componente** | contrato + experiencia + accesibilidad de cada pieza | blanda / dura en release |
| 9 | **Recorridos contra la pila real, sin mocks** | lo que solo falla con todo levantado | blanda / dura en release |
| 10 | **Matriz de banderas** | que encender una opción no tumba el producto | dura |
| 11 | **Caos y carga** | reinicio, dependencia caída, SLO | blanda / release |

### 4.3 Los tests-contrato son el corazón

Un **test-contrato** comprueba una propiedad **estructural** del repositorio, no
un comportamiento. Se escriben con AST —sin importar el módulo, sin base de
datos, sin red— y son baratísimos. Los que hay que tener desde el día 0:

1. **Las capas no se filtran**: la de aplicación no importa la de entrada; el
   dominio no importa nada de arriba; los puertos no conocen a quien los
   implementa; los adaptadores de persistencia no conocen la capa de aplicación.
2. **No hay ciclos de importación en cabecera.** Escrito **cuando el grafo está
   limpio**: un contrato que entra en verde no arrastra deuda, solo impide la
   primera violación.
3. **Toda ruta que muta estado exige autenticación**, salvo una allowlist
   explícita escrita a mano.
4. **Todo elemento del enum está registrado en su tabla de despacho.** Añadir un
   caso sin registrarlo es un rojo, no un fallo en tiempo de ejecución.
5. **Los catálogos espejados coinciden** (el del servidor y el de la interfaz).
6. **Los mapas de navegación dicen la verdad** (§3.3).
7. **El módulo que autoriza no importa el módulo de las listas del usuario**
   (P12). Una garantía de diseño que se comprueba **leyendo el código**.
8. **Lo generado no depende del reloj ni del entorno**: dos ejecuciones producen
   el mismo artefacto.

Detalle fino que importa: los contratos de ciclos cuentan **solo los imports de
cabecera**, porque el import perezoso dentro de un método es la *solución*
deliberada al ciclo, no el ciclo — marcarlo sería castigar el arreglo (P1). Pero
para la métrica de **acoplamiento** el perezoso **sí** cuenta, porque acopla
igual. Son dos preguntas distintas sobre el mismo import y cada medida responde
la suya.

### 4.4 La ejecución en seco es de diseño, no un modo de prueba

Que el sistema entero pueda correr **sin red, sin claves y sin coste** no es una
comodidad: es lo que permite que la suite ejercite el motor de verdad. Se
consigue **por los puertos**, inyectando adaptadores simulados en la frontera, y
tiene dos reglas:

- **En seco no se toca el mundo.** Ningún efecto exterior, ni siquiera uno
  «inofensivo».
- **Pedir un proveedor real sin su credencial falla en voz alta.** Jamás degrada
  al simulado en silencio: una degradación silenciosa convierte una suite verde
  en una suite que no prueba nada.

### 4.5 Cobertura: se mide, se blinda y se desconfía

La cobertura se mide **en la misma pasada de la suite** (una segunda pasada
duplica el paso más caro) y se blinda con un ratchet. Y se acompaña siempre de
la advertencia que OM aprendió a su costa: **la cobertura mide líneas
ejecutadas, no verificación**. Allí una suite en verde con cobertura alta nunca
había mirado el cuerpo HTTP que salía hacia un sistema externo. De ahí la clase
de prueba que lo cierra: **toda salida al exterior declara la forma de lo que
manda**, y hay una prueba que compara el envío real contra esa forma.

El listón se pone **donde se está**, no donde se querría: un umbral alto de golpe
produce pruebas de relleno, que es peor que una cobertura honesta más baja. Y
unas décimas de margen si hay pruebas que se saltan solas al faltar una
herramienta — un ratchet que da falsos rojos se acaba desactivando (P1).

### 4.6 Lo que no se puede probar en una máquina de CI

Aprendizaje de una persona nueva, una alerta llegando a un buzón, una carga
contra un clúster. **Se mide con personas y con entornos reales, y la medición
caduca** (P5). El registro de mediciones (§9.3) es la única defensa posible para
esa clase de característica: el número envejece y la compuerta se pone roja sola.

---

## 5. Arquitectura del backend (hexagonal)

### 5.1 Las capas y la única regla

Las dependencias apuntan **hacia adentro**: `api → services → domain`. Nunca al
revés.

| Capa | Carpeta | Qué puede importar |
|---|---|---|
| **Dominio** — entidades y reglas, `@dataclass`, sin framework ni BD | `app/domain/` | nada de arriba |
| **Puertos** — interfaces abstractas | `app/ports/` | dominio |
| **Adaptadores de persistencia** — traducen a dominio en la frontera | `app/repositories/` | dominio, puertos, modelos |
| **Aplicación** — orquestación y casos de uso | `app/services/` | todo menos `api` |
| **Entrada** — routers, sin lógica de negocio | `app/api/` | todo |

Cada prohibición de esa tabla tiene su test-contrato (§4.3). No es una
recomendación en un documento: es una compuerta.

### 5.2 Los puertos son pequeños y se nombran por lo que hacen

En OM: `event_sink`, `secret_resolver`, `tool_runner`, `document_parser`,
`object_storage`, `vector_store`, `chat_channel`, `ticket_system`,
`browser_engine`, `workspace_fs`, `observability`. Ninguno tiene más de un puñado
de métodos (la letra **I** de SOLID: segregación de interfaces, §7).

Tres reglas sobre puertos que costaron caro aprender:

- **Lo que ejecuta código de terceros vive fuera del proceso que custodia los
  secretos.** Un motor de navegador ejecuta JavaScript ajeno; ese es el último
  proceso que interesa dentro del que tiene el vault. El puerto se queda dentro;
  el motor, en un proceso aparte.
- **El identificador de aislamiento va en el puerto y es obligatorio** (P11). En
  OM, el espacio vectorial exige `tenant` en su `Namespace`, y **ningún servicio
  compone un nombre de colección**: de que ese nombre estuviera bien compuesto
  dependía el aislamiento entre clientes.
- **Poner algo detrás de un puerto sube el acoplamiento medido, y está bien.** La
  cifra sube porque la dependencia **dejó de ser invisible** (antes se importaba
  una biblioteca externa, que no se contaba). Eso es lo contrario de una fuga, y
  el motivo del ratchet lo dice con todas las letras.

### 5.3 Contra el god-module

El motor de OM se descompuso en colaboradores de responsabilidad única (topología,
despacho, composición de prompt, artefactos, bucles, trazas). Lo que vale para
cualquiera:

- **La costura se busca por afinidad de dependencias**, y el número de miembros
  del protocolo extraído dice si la costura era una costura. Si el protocolo
  necesita doce métodos, no había costura.
- **Extraer sin criterio produce el mismo god-module con otro nombre.** Por eso
  el ratchet mide **acoplamiento total** además del máximo por fichero: si no,
  el techo por fichero se esquiva repartiendo la deuda entre diez ficheros nuevos.
- **El techo de tamaño se sube a mano y se ve en el diff** (P4, P15).
- **El import perezoso dentro de un método es un anti-ciclo deliberado.** Se
  documenta en un ADR para que nadie lo «arregle» subiéndolo a la cabecera.

### 5.4 Migraciones

Herramienta de migraciones desde el día 0, y **compuerta de no-drift**: base
efímera → `upgrade head` → comparar contra los modelos. Una columna añadida al
modelo sin su revisión es un rojo. Cualquier mecanismo legado de
«añadir-columna-al-vuelo» se declara **legado** en un ADR y no admite entradas
nuevas.

Y la otra mitad, la que casi nadie escribe: **qué borra cada marcha atrás**. Se
genera del propio código de migraciones, de modo que lo único que puede fallar es
no regenerarlo — y entonces el documento diría que volver atrás cuesta menos de
lo que cuesta, que es la peor forma de equivocarse en esto.

### 5.5 Banderas de función, apagadas por defecto

- **Que una función exista en el código no significa que esté activa.** Catálogo
  explícito en un módulo, con inventario auditado.
- **Hay dos usos de una bandera y no se pueden mezclar**: la de **capacidad**
  («este tipo de cosa no existe aquí») puede esconder la pieza y hacer fallar su
  despacho; la de **comportamiento** («dentro de algo que sí existe, esta rama»)
  no puede ninguna de las dos. El mapa es **explícito** —deducirlo de los `if`
  reparte respuestas falsas en los dos sentidos— y la comprobación va en **el
  punto único de despacho**, no repetida en cuarenta y cinco manejadores.
- **Esconder no es apagar.** Que la interfaz no ofrezca algo no es un control de
  seguridad: la petición puede llegar por la API.
- **Matriz de banderas** como compuerta dura: un eje **aislado** por bandera
  encendida (no combinatoria), que comprueba que encenderla no tumba el producto
  y que revertirla devuelve el sistema a su reposo.

---

## 6. Arquitectura del frontend (por capas)

### 6.1 Las cuatro capas y la frontera única

```
components/     →     app/page.tsx     →     hooks/     →     lib/
(presentación         (orquestador:          (lógica)         (ÚNICA frontera
 controlada)           cablea estado                           con el backend)
                       y hooks)
```

- **Los componentes son controlados**: props y callbacks, sin I/O propio.
- **Ningún componente de vista importa el cliente HTTP**: pasa por un hook.
- **`lib/` es la única capa que toca el exterior**: cliente REST tipado, socket,
  autenticación, utilidades puras.

Esto es hexagonal con otro vocabulario: `lib/` son los adaptadores, los `hooks`
son los casos de uso, los componentes son la vista, y la inversión de
dependencias se consigue pasando callbacks hacia abajo.

### 6.2 Cómo se blinda una regla que «es la que más se rompe»

La combinación de tres cosas, y ninguna sola habría bastado:

1. **Se dice donde se escribe el import**: regla de lint como **aviso**, con el
   mensaje explicando la capa y citando el ratchet.
2. **Se cuenta**: un ratchet con el número exacto de componentes que hoy la
   incumplen (en OM, 33 de 71). No exige arreglarlos; **impide que mañana sean
   34**.
3. **Se declara la retirada**: cuando el contador llegue a cero, el aviso sube a
   error y el ratchet se retira. Está escrito en el propio ratchet.

Por qué aviso y no error: 33 componentes a reescribir en un PR es un rojo
inarreglable, y un rojo inarreglable se desactiva (P1).

Y la disciplina de separar magnitudes: en OM quedaban además 4 imports invertidos
de tipos, **medidos aparte a propósito** — mezclarlos en un número haría que
arreglar una fuga tapara el empeoramiento de la otra.

### 6.3 Reglas de interfaz que valen en cualquier proyecto

- **Nada de diálogos nativos del navegador** (`confirm`/`alert`/`prompt`): un
  diálogo nativo **bloquea el hilo**, y con una ejecución en vivo en pantalla eso
  congela la traza. Se usa un proveedor de diálogos propio.
- **Accesibilidad con tokens**, no con colores sueltos: pares de color validados
  para contraste WCAG 2.1, nombre accesible obligatorio en los controles de solo
  icono, y una auditoría determinista (sin navegador) como compuerta blanda.
  La auditoría estática **no ve** lo que depende del color heredado ni el nombre
  de un control que solo existe tras hidratar: para eso van los recorridos con
  motor de accesibilidad sobre la aplicación levantada, en la compuerta de
  release.
- **Adopción gradual del tipado estricto, por olas**: los errores reales
  bloquean; las reglas de alto volumen entran como aviso y suben a error familia
  por familia. La lista de las que faltan está escrita en la propia configuración,
  con el motivo.
- **Una regla desactivada se justifica en el sitio**, con el número de falsos
  positivos que produjo. Sin eso, en seis meses nadie sabe si se puede reactivar.
- **Un tema gobierna cómo se ve algo y cuándo aparece; nunca qué se puede hacer,
  dónde está ni en qué orden.** Un tema capaz de esconder una acción es un segundo
  producto. Con test-contrato sobre el CSS y sobre los componentes.

---

## 7. SOLID con mecanismo

SOLID no se cumple por escribirlo en un documento. Cada letra necesita un
mecanismo y un verificador:

| | Principio | Mecanismo concreto | Cómo se verifica |
|---|---|---|---|
| **S** | Responsabilidad única | Un servicio por asunto; los motores grandes descompuestos en colaboradores con nombre | Ratchet de tamaño de fichero + ratchet de acoplamiento |
| **O** | Abierto/cerrado | Despacho **dirigido por datos**: `tipo → manejador` en un registro; añadir un caso es **una entrada en la tabla**, sin tocar el bucle | Test-contrato: todo elemento del enum está en el registro |
| **L** | Sustitución de Liskov | Adaptadores intercambiables por su puerto; la suite inyecta simulados sin tocar el núcleo | La suite corre entera en seco |
| **I** | Segregación de interfaces | Puertos pequeños y enfocados, nunca una interfaz gorda | Revisión del nº de miembros al extraer un protocolo |
| **D** | Inversión de dependencias | El motor **recibe** sus puertos por inyección, con adaptadores por defecto | Tests-contrato de capas: el dominio no conoce la infraestructura |

Dos corolarios que en OM ahorraron más tiempo que los cinco principios juntos:

- **Si añadir un caso obliga a tocar más de un sitio, la tabla de despacho está
  incompleta.** El coste de añadir es la métrica de la letra O.
- **Si una prueba necesita mockear la red, la capa está mal puesta.** El coste de
  probar es la métrica de la letra D.

---

## 8. Seguridad: OWASP, OWASP API, CWE Top 40

### 8.1 El mapeo de cumplimiento, con evidencia trazable

Un documento (`docs/security/CUMPLIMIENTO.md`) que recorre **cuatro marcos**
—OWASP Top 10, OWASP API Security Top 10, CWE Top 40 (Top 25 + los 26-40 «on the
cusp») y NIST AI RMF— y por cada categoría dice **qué control la cubre, dónde vive
y qué prueba lo demuestra**, citando rutas reales.

Lo que lo hace útil en vez de decorativo:

- **Cuatro estados, y uno de ellos es «Pendiente»**: *Cubierto* (hay control **y**
  prueba que lo ejercita), *Parcial* (hay control con un límite que se enuncia),
  *Pendiente* (no hay control; se dice, no se maquilla), *No aplica* (con el
  porqué).
- **Los huecos van primero, no al final.** «Ponerlos al final sería esconderlos»:
  una tabla con los cuatro o cinco que un revisor externo señalaría antes que
  nada, con su riesgo y las categorías que tocan.
- **Compuerta dura**: un script comprueba que **toda ruta citada existe** y que
  las cuatro secciones siguen presentes. Lo que explícitamente **no** comprueba
  —y se dice cada vez— es que el control siga siendo correcto: de eso se encargan
  las pruebas citadas, que corren en la misma compuerta.
- **Declara qué no es**: «esto es un mapeo de controles, no una auditoría; no lo
  ha revisado un tercero, no hay pentest, y quien lo escribió es quien escribió
  el código que evalúa». Un mapeo dice *qué se hizo a propósito*; una auditoría
  dice *si funciona*.

Un documento de cumplimiento con evidencia que ya no está **es peor que no
tenerlo**, porque hay un papel afirmando algo que dejó de ser cierto. Por eso la
compuerta es dura.

### 8.2 Controles mínimos por categoría (lo que OM implementó y es portable)

**Acceso (A01, A05 API, CWE-862/863/639/269)**
- Autorización por rol **y** por objeto: el identificador no basta, se comprueba
  propiedad.
- **Test-contrato: toda ruta que muta estado exige sesión**, salvo allowlist
  explícita escrita a mano y revisada.
- Política de autoridad por **radio de impacto** de la operación, no solo por rol.
- **El perímetro sin autenticación se audita como hostil**: las rutas públicas
  (webhooks, salud, enrolamiento) reciben *fuzzing* propio y limitador propio.

**Criptografía y secretos (A02, CWE-798/522/312)**
- **Vault**: los secretos se referencian **por nombre**; el valor se descifra en
  el proceso padre y **jamás** se escribe en el código, en un prompt, en un
  ejemplo ni en una traza.
- **Compuerta de higiene de secretos** sobre lo que git **versiona de verdad**
  (`git ls-files`, no el disco): ningún fichero de entorno salvo plantillas
  `.example`, ninguna base de datos, ningún patrón de credencial real
  (claves de nube, tokens de proveedores, bloques de clave privada). Excluye
  ficheros de prueba y plantillas, donde los valores simulados son legítimos.
  En OM esta compuerta nació porque un `git add -A` se llevó una base de datos
  entera al repositorio — y una base del producto contiene la tabla de usuarios y
  la de secretos.
- **La credencial se ata al vínculo, no al entorno**: un token en el fichero de
  entorno significa una sola credencial para todos los clientes, rotación que
  exige tocar el servidor y reiniciar, y el secreto en claro en el disco del host.

**Inyección (A03, CWE-89/78/77/94/74/20)**
- ORM con parámetros ligados; sin concatenación de consultas.
- Ejecución de mandos: **lista blanca con bloqueo de encadenado**, y **nunca**
  `shell=True`.
- Código de usuario: guardia estático *default-deny* de módulos, límites de
  recursos y sandbox.
- **El alcance se valida sobre la forma canónica, nunca sobre la cadena escrita.**
  Si el mismo objeto se puede escribir de cinco maneras, validar el texto es
  validar la etiqueta: se canonicaliza y se valida por prefijo de la forma
  numérica.
- Esquemas explícitos de entrada **y salida** en toda la frontera HTTP: lo no
  declarado no entra ni sale.
- XML de fuentes externas con biblioteca endurecida.

**Serialización (CWE-502)**
- **JSON en todas las fronteras**; el módulo de serialización nativa, vetado en el
  guardia estático.

**Consumo de recursos (A04/API4, CWE-400/770)**
- Control de admisión con techo por proceso, espera acotada y contrapresión
  (`429`), temporizadores por unidad de trabajo y por ejecución completa,
  presupuesto de coste y de contexto, límite de tamaño en las subidas.
- **Un umbral sobre cero peticiones no es un umbral**: toda alerta de tasa lleva
  un mínimo de volumen debajo.

**SSRF (A10/API7, CWE-918)**
- Guardia dedicada que rechaza direcciones privadas, reservadas y multicast.
- **Un destino externo es un recurso registrado por un administrador**, y ese
  registro **es** la lista de destinos permitidos. Una URL libre en un formulario
  es SSRF con más pasos.

**Travesía de rutas y subidas (CWE-22/434/427/732)**
- Patrón estricto del nombre **más** comprobación de que la ruta resuelta sigue
  dentro del directorio publicado.
- Extensión mapeada a un tipo conocido, tamaño máximo, y escritura **fuera** de
  cualquier ruta ejecutable del servidor.

**Trazas y registro (A09, CWE-532/209)**
- Enmascarado de secretos **antes** de escribir, no al mostrar.
- Traza por ejecución persistida, métricas, y vigilantes de salud.
- **Un barrido de trabajos zombis no puede correr solo al arrancar**: un barrido
  que solo corre al arrancar no ve lo que el arranque acaba de romper.

**Integridad (A08)**
- Artefactos descargables publicados **con su huella a la vista** y servidos solo
  si el nombre casa un patrón estricto.
- Compuerta de no-drift de migraciones.
- **La huella del contenido decide si hay que recompilar un artefacto**, no el
  número de versión del producto —que sube aunque ese componente no cambie, y por
  eso avisa en falso y puede callar cuando importa—.

**Dependencias y licencias (A06)**
- Auditoría de dependencias en las tres cadenas de herramientas del proyecto.
  **Bloquea lo que tiene arreglo** (severidad alta **y** parche disponible); lo
  que no tiene parche **exige declararse** en un registro con motivo y fecha de
  revisión (P1).
- Una excepción **caducada informa, no corta**: forzar el bloqueo por una fecha
  convierte el registro en un enemigo y el resultado previsible es que alguien
  escriba el año 2099.
- Si la cadena tiene una herramienta que distingue **lo que el código llama** de
  lo que solo está en el árbol, el filo se afina: bloquea lo alcanzable, informa
  del resto.
- **Compuerta de licencias**: hablar con un sistema por HTTP es interoperabilidad;
  **enlazar** su cliente con copyleft fuerte contamina un producto comercial. La
  spec sola no basta: hay compuerta.

### 8.3 Cuando hay un modelo de lenguaje en el sistema (NIST AI RMF / MITRE ATLAS)

Estos ocho controles no están en OWASP y son los que deciden si un sistema
agéntico es defendible:

1. **Todo lo que entra en un prompt sin haberlo escrito el sistema es dato
   citado** (P10): delimitado, etiquetado y escaneado **al guardar**, no al
   componer. Incluye salida de herramientas, memoria recuperada, documentos
   ingeridos y manifiestos importados.
2. **Escáner de contenido no confiable** en las dos direcciones: hacia el modelo
   (inyección de prompt) y hacia fuera (secretos y datos personales).
3. **Redacción reversible de datos personales** antes de salir del perímetro.
4. **El código que el sistema fabrica se prueba antes de persistirse**: contrato
   primero, guardia estático *default-deny*, y casos de prueba obligatorios. No
   hay atajo por venir «de un repositorio conocido».
5. **Autonomía acotada por presupuesto**, con arnés corregible: el bucle tiene
   techo de pasos, de coste y de tiempo, y un interruptor de parada.
6. **Herramientas externas con política por anotación**, no con confianza.
7. **La elección del modelo se decide antes de inferir (por coste) y el suplente
   se usa después (por fallo)**: enrutar y sobrevivir son dos problemas distintos.
8. **Un juez automático evalúa la composición**, no solo cada pieza; y sus
   veredictos se contrastan contra los registros que el producto escribe de
   verdad.

### 8.4 Aislamiento entre clientes

Si el producto sirve a varios clientes, cuatro cosas se parten o no hay
aislamiento — **el envase no es lo que aísla**:

1. **El almacenamiento** (espacio de nombres obligatorio en el puerto, resuelto
   en el servidor: P11).
2. **La cola de trabajo** (si es común, el trabajo de un cliente llega al
   trabajador de otro).
3. **Los secretos** (por vínculo, no globales).
4. **El usuario del sistema operativo** que ejecuta el código del cliente. En OM
   esto se resolvió con un binario **setuid minúsculo y auditable** como **único**
   componente privilegiado: el backend **pide** el cambio de usuario en vez de
   tenerlo. Sus pruebas son sobre todo **de rechazo** —directorio fuera del home,
   cliente inexistente, binario del sistema— y corren en la compuerta dura: un
   componente privilegiado con un fallo de validación de rutas es peor que no
   tenerlo, porque añade una ruta privilegiada sin quitar ninguna.

### 8.5 La configuración también es superficie de ataque

El análisis estático audita el código y el auditor de dependencias audita las
bibliotecas, pero **el artefacto guardado —la configuración que el usuario creó—
no lo audita nadie**. Un comando `posture-check` revisa la postura **en reposo**
(secretos, permisos, superficie pública, integraciones, zona de ejecución) y sale
distinto de cero ante un hallazgo crítico. Es compuerta de release, no de *push*.

---

## 9. Calidad medible: ratchets, madurez, mediciones, promesas

Cuatro registros, el mismo mecanismo (§3.4) y cuatro preguntas distintas.

### 9.1 Ratchets — lo que no puede empeorar en silencio

`docs/ratchets.yaml`. Campos: `id` estable · `nombre` · `medida` (la función que
la calcula) · `liston` · `direccion` (`menor_mejor` / `mayor_mejor`) · `motivo`
obligatorio · `aviso_holgura` opcional.

Los siete que OM acabó teniendo, como punto de partida razonable para cualquier
proyecto:

| Magnitud | Dirección | Por qué |
|---|---|---|
| Acoplamiento máximo de un fichero | menor | el god-module vuelve por acumulación |
| **Acoplamiento total** | menor | sin la suma, el techo por fichero se esquiva creando ficheros |
| Cobertura de la suite | mayor | se degrada sola, entrega a entrega |
| Módulos con tipado estricto | mayor | las olas de tipado se paran solas si nadie cuenta |
| Violaciones graves de accesibilidad | menor | cero, y **en un solo listón**: separarlas permitiría cambiar una crítica por tres graves sin mover el número |
| Pasos de los recorridos principales | menor | «si una versión necesita el doble de clics, que se vea» |
| Componentes que se saltan la capa | menor | la regla que más se rompe, por fin contada |

Detalles que deciden si el mecanismo vive o muere:

- **`aviso_holgura`**: avisa cuando sobra margen. Mejorar sin mover el listón
  regala lo ganado a la entrega siguiente.
- **El `motivo` se amplía, no se reescribe**, cada vez que el listón se mueve: la
  historia de por qué subió tres puntos es el documento más útil del repositorio
  cuando alguien propone «limpiar el acoplamiento».
- **Lo que depende de la máquina no lleva listón** (tiempos de ejecución, por
  ejemplo): se publica, pero un ratchet con falsos rojos se desactiva (P1).

### 9.2 Registro de madurez — qué nivel tiene cada capacidad

`docs/madurez.yaml`, con la rúbrica que hace el trabajo:

| Nivel | Nombre | Significa |
|---|---|---|
| 0 | ausente | no existe la capacidad |
| 1 | declarada | está en un documento o un ADR; nada la ejecuta |
| 2 | implementada | existe y funciona; nadie comprueba que siga |
| 3 | **verificada** | hay prueba automática, aunque sea señal blanda |
| 4 | **blindada** | la prueba es **compuerta dura**: romperla bloquea el push |
| 5 | **medida** | número, fecha y umbral en entorno real, con ratchet o SLO |
| — | no evaluada | no hay evidencia que lo sostenga, y se dice |

Reglas: la evidencia es **obligatoria desde el 3 y tiene que resolver** (el
fichero o la prueba existen de verdad); el **4 exige una evidencia de tipo
compuerta**; el **5 exige una medición del registro §9.3**. Y `scope`, `no_cubre`
y **`brecha`** son obligatorios — la brecha en una frase accionable es lo que
convierte el registro en trabajo en vez de en un cuadro de mandos.

**El registro bloquea la mentira, no la ignorancia**: un `2` honesto vale más que
un `4` sin prueba. Y una corrección que OM tuvo que hacerse a sí misma: **un
registro con todo en 5 deja de discriminar y pasa a ser otra cosa** — si la nota
media sube sin que nadie mida, la rúbrica se ha convertido en autoestima.

### 9.3 Registro de mediciones — los números que sostienen un 5

`docs/mediciones.yaml`. Campos **todos obligatorios**: `id` · `caracteristica`
(a qué capacidad sostiene) · `nombre` · `valor` · `unidad` · `umbral` ·
`direccion` · `fecha` (cuándo se **midió**, no cuándo se escribió) ·
`caduca_en_dias` · `como` (cómo se reproduce; tiene que resolver a un comando o
a una ruta real) · `entorno` (un número sin entorno no se puede comparar) ·
**`no_dice`** (qué **no** dice; es lo que distingue un dato de una cifra de
portada).

Dos decisiones no obvias:

- **Tope de caducidad**: una caducidad muy larga es no tenerla.
- **Vencimientos escalonados a propósito**, con valores no redondos. Con todas a
  90 o 180 días, diecinueve vencían **el mismo día** — y un registro que pide
  diecinueve mediciones la misma semana no se atiende: se ignora. Se conserva la
  *banda* de cada una (lo que se degrada con el código, lo que se degrada con el
  entorno) y se separan los vencimientos dentro de ella.

### 9.4 Registro de promesas — lo que se le dice a quien usa el producto

`docs/promesas.yaml`. Alcance declarado: las **promesas de portada** (el README,
la guía de inicio, las descripciones de las banderas), no toda frase del
repositorio. Campos: `claim` (la frase tal cual se dice) · `source` (dónde se
afirma) · `verifier` (que resuelva) · `kind` · `status`
(`verificada` / `no_verificada` / `desmentida`) · `scope` · `not_checked`
(obligatorio si está verificada) · `motivo` · `flag`.

`desmentida` es un estado legítimo y publicable: **la documentación lo afirma y
la prueba dice que no**. Ese estado es el que hace que el registro valga algo.

---

## 10. Catálogo de compuertas

La foto de OM al cerrar la fase 248. La columna «portable» marca lo que tiene
sentido en cualquier proyecto desde el día 0.

### Duras — bloquean el *push* (14)

| Trabajo | Qué comprueba | Portable |
|---|---|---|
| `backend` | lint · tipos · suite **con cobertura** · ratchets de magnitud | ✅ |
| `frontend` | tipos · lint · pruebas unitarias · compilación | ✅ |
| `tech-debt` | ningún marcador de deuda al inicio de un comentario | ✅ |
| `secrets` | higiene de secretos sobre lo versionado | ✅ |
| `migrations` | no-drift del esquema | ✅ |
| `adr-gate` | disciplina de ADR ante sentinelas estructurales | ✅ |
| `licenses` | sin copyleft fuerte enlazado en el producto | ✅ |
| `dependencias` | vulnerabilidades **con arreglo**, en todas las cadenas | ✅ |
| `docs` | 13 subcomprobaciones de integridad documental + wiki estricta | ✅ |
| `flags` | matriz de banderas, un eje aislado por bandera | ✅ |
| `mediciones` | los números siguen vigentes (caducidad) | ✅ |
| `edge-binarios` | los artefactos publicados son del código de hoy | si hay artefactos |
| `edge-agent` | vet · pruebas · compilación estática del componente en Go | si hay Go |
| `lanzador` | el componente privilegiado: pruebas de **rechazo** | si hay privilegio |

### Blandas — informan (10)

`security` (análisis estático con línea base + auditoría) · `performance` (SLO
con carga) · `qa-nodes` (arnés por componente) · `eval` (escenarios end-to-end) ·
`a11y` (contraste y nombres accesibles) · `journeys` (recorridos contra la pila
real) · `caos` (reinicio, base caída, proveedor sin clave) · `k3d` (los planos de
despliegue siguen aplicando) · `smoke-onboarding` · `smoke-metrics`.

### De release — condición para promover (5)

Arnés por componente en **duro** · auditoría de postura en reposo · SLO de
rendimiento con carga real · recorridos con motor de accesibilidad sobre la
aplicación levantada · ratchets en modo estricto.

**Las tres subcomprobaciones documentales que más rinden**, si solo caben tres:
que el control de trabajo esté sincronizado, que **la evidencia citada exista**,
y que **lo generado coincida con su generador**.

---

## 11. Kit de arranque (el día 0)

Antes de la primera línea de producto. Cuesta una tarde y es la tarde mejor
invertida del proyecto:

```
AGENTS.md                      # mapa en frío (§3.3)
CLAUDE.md                      # su desarrollo por capas
README.md                      # qué es, cómo se arranca, dónde está cada cosa
SECURITY.md                    # modelo de amenazas + controles
Makefile                       # install · run · ci · hooks · docs · release-check
scripts/
  ci_local.sh                  # LA compuerta, con jobs seleccionables y --no-soft
  install_hooks.sh             # core.hooksPath → hooks versionados
  hooks/pre-push               # delega en --no-soft; NO mantiene su propia lista
  check_tech_debt.sh
  check_secrets_hygiene.sh
  check_adr_gate.sh
  check_ratchets.py
docs/
  SPEC_RAIZ.md                 # este documento
  adr/README.md + 0001-…       # el primero es la decisión sobre la compuerta
  ratchets.yaml                # vacío el día 0; se llena al medir
  promesas.yaml
  madurez.yaml
  mediciones.yaml
  security/CUMPLIMIENTO.md     # los cuatro marcos, con «Pendiente» donde toca
  EXTENDING.md                 # cómo añadir cada tipo de pieza, paso a paso
  fases/estado_fases.csv       # control (separador ;), fuente canónica
backend/
  app/{domain,ports,repositories,services,api}/
  tests/{arquitectura,contratos}_test.py     # los 8 contratos del §4.3
  mypy.ini · pytest.ini
frontend/
  AGENTS.md                    # anidado, con precedencia
  src/{components,hooks,lib,app}/
  eslint.config.mjs            # con el ratchet de frontera declarado
```

**Orden de adopción** (una ola por semana, no todo el primer día):

1. **Semana 1** — compuerta local + hook + las tres compuertas baratas
   (deuda, secretos, tipos). Sin esto, lo demás no se sostiene.
2. **Semana 2** — capas y sus tests-contrato, **mientras el grafo está limpio**.
   Un contrato escrito en verde no arrastra deuda; escrito en rojo, nace
   desactivado.
3. **Semana 3** — ADR 0001 (la compuerta) y `adr-gate` con dos o tres sentinelas.
4. **Semana 4** — ejecución en seco hermética y el primer registro (promesas).
5. **Cuando haya algo que medir** — ratchets con el listón **donde se está**.
6. **Cuando haya usuarios** — madurez, mediciones y el mapeo de cumplimiento.

### Lo que NO conviene copiar de OM

Honestidad hacia los dos lados (P3):

- **199 ficheros de spec y un consolidado de 248 fases.** El control y las specs
  valen; el consolidado gigante es un artefacto del historial, no un método.
- **87 ADRs.** El número es consecuencia de 248 fases, no un objetivo. Un ADR por
  decisión **estructural**; si se escriben dos por semana, se está documentando
  el *qué* y no el *porqué*.
- **La ausencia de CI remota.** Fue una decisión **de coste**, medida y confirmada
  con números (ADR 0001), no una preferencia técnica. Con presupuesto, la
  compuerta va en el servidor y el hook queda como segunda línea.
- **Las 13 subcomprobaciones del trabajo `docs`.** Nacieron una a una, cada vez
  que un documento envejeció en silencio. Se añaden cuando duele, no por
  adelantado.
- **Un fichero de seguridad de 57 000 caracteres.** Lo que se consulta de verdad
  es el mapeo con evidencia (§8.1) y los ADRs.

---

## 12. Antipatrones observados y su cura

| # | Antipatrón | Cómo se manifestó | Cura |
|---|---|---|---|
| 1 | **La fuga lenta** | 736 líneas se colaron en un fichero sin que ninguna entrega lo empeorara de forma llamativa | Ratchet de magnitud (P4) |
| 2 | **El gate inarreglable** | un auditor en duro choca con lo que no tiene parche y acaba comentado | Filo «grave **y** con arreglo» + registro de excepciones (P1) |
| 3 | **Dos listas que divergen** | el hook corría 7 trabajos y la compuerta 12: cinco duras no bloqueaban nada | Una sola definición + prueba que impide la segunda (P8) |
| 4 | **El documento que envejece** | un mapeo citando pruebas renombradas; un manual publicado dos versiones atrás | Compuerta que comprueba que la evidencia existe y que lo generado coincide |
| 5 | **La prueba que nunca corrió** | ~485 pruebas del frontend fuera de toda compuerta; dos en rojo durante semanas | Prueba-contrato que comprueba **qué corre la compuerta** |
| 6 | **Cobertura confundida con verificación** | suite verde que jamás miró el cuerpo HTTP que salía | Contrato de forma en toda salida al exterior |
| 7 | **El código muerto documentado** | una función escrita, documentada y **jamás llamada** durante 50 fases | Prueba de camino completo, no de unidad |
| 8 | **El verde que mentía** | un canal de registro que nunca se escribió: dos consumidores leían el vacío | Verificar de extremo a extremo, no por componente |
| 9 | **La cifra sin entorno** | un número de experiencia de desarrollo medido una vez, citado durante meses | Medición con fecha, entorno y caducidad (P5) |
| 10 | **La nota que sube sola** | un registro de madurez con todo en 5 | Evidencia obligatoria por nivel y reauditoría con vencimientos |
| 11 | **El default cambiado** | cambiar un valor por defecto reinterpretó en silencio todas las filas antiguas | Migración explícita (P13) |
| 12 | **El permiso editable** | un campo del editor que podía **ampliar** quién ejecuta | Las listas del usuario solo restringen, con prueba de no-import (P12) |

---

## 13. Listas de comprobación

### 13.1 Antes de abrir un PR

- [ ] La compuerta local está **verde** (no «verde salvo un trabajo»).
- [ ] Si toca una decisión estructural: **su ADR está en este mismo PR**.
- [ ] Si mueve un listón: el `motivo` del ratchet lo explica y **se amplía**, no
      se reescribe.
- [ ] Si abre superficie nueva: el limitador, el escudo y el corte entran aquí
      (P14).
- [ ] Si añade un caso a un enum: está en la tabla de despacho **y** en el
      test-contrato.
- [ ] Si añade una promesa de portada: tiene entrada en el registro con
      verificador, o `status: no_verificada` con motivo.
- [ ] Si cambia un valor por defecto: hay migración explícita de lo existente.
- [ ] El diff no incluye nada que no se haya mirado (`git add -A` es el enemigo).

### 13.2 Antes de cerrar una fase

- [ ] La spec existe, con **hallazgo que decide el diseño** y **lo que NO entra**.
- [ ] El control tiene su fila **ahora** (no antes), con hallazgo y enmiendas.
- [ ] El título técnico es idéntico en los cuatro sitios.
- [ ] Los ADR nuevos están en el índice y citados desde los mapas.
- [ ] Los registros afectados (madurez, mediciones, promesas, ratchets) están al
      día, con `scope`, `no_cubre` y `brecha`.
- [ ] El capítulo de novedades de la versión publicada existe.
- [ ] La compuerta de release pasa antes de promover.

### 13.3 Al añadir una pieza nueva (nodo, adaptador, integración)

- [ ] Servicio en la capa correcta, sin importar hacia arriba.
- [ ] Entrada en el enum **y** en el registro de despacho.
- [ ] Contrato claro: devuelve su tipo; **un fallo de negocio es una excepción**,
      nunca un diccionario de error silencioso.
- [ ] Catálogo y espejo de la interfaz actualizados (y su prueba de espejo).
- [ ] Clave añadida al test-contrato de despacho.
- [ ] Accesibilidad comprobada si tiene interfaz.
- [ ] Documentación de extensión actualizada en el mismo PR.

---

## Cierre

Todo lo anterior se reduce a una operación repetida: **convertir una intención en
un mecanismo, y el mecanismo en una compuerta que ofrece dos salidas**. Lo que no
tiene mecanismo se erosiona; lo que tiene un mecanismo sin salidas se desactiva;
y lo que tiene compuerta y salidas **sobrevive a quien lo escribió**, que es la
única definición útil de calidad en un proyecto que va a durar más de un año.

> Y la regla que gobierna a este propio documento: si una de estas reglas se
> cambia en un proyecto, **se cambia aquí y se dice por qué**. Una spec-raíz que
> no se actualiza es el antipatrón nº 4 aplicado a sí misma.
