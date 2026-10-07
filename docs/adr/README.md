# Índice de ADRs

Se lee antes de proponer un cambio estructural. Un ADR no se reescribe: se le añaden actualizaciones fechadas al pie.

| N.º | Decisión | Estado |
|---|---|---|
| [0001](0001-la-compuerta-vive-en-el-repositorio.md) | La compuerta vive en el repositorio: `ci_local.sh` + pre-push versionado | Aceptado |
| [0002](0002-el-copyleft-se-estudia-no-se-copia.md) | El copyleft se estudia, no se copia (proyecto MIT) | Aceptado |
| [0003](0003-el-rtl-no-tiene-razon-la-tiene-el-modelo-bit-exact.md) | El RTL no tiene razón: la tiene el modelo bit-exact | Aceptado |
| [0004](0004-la-microsd-almacena-no-retarda.md) | La microSD almacena, no retarda (todo el audio en BSRAM) | Aceptado |
| [0005](0005-2048-ciclos-exactos-valen-mas-que-48-khz-exactos.md) | 2 048 ciclos exactos valen más que 48 kHz exactos (fs = 48 828 Hz) | Aceptado |
| [0006](0006-los-efectos-son-programas-no-modulos-rtl.md) | Los efectos son programas, no módulos RTL (núcleo tipo FV-1) | Aceptado |
| [0007](0007-el-espanol-es-la-fuente-y-las-traducciones-llevan-sello.md) | El español es la fuente; las traducciones llevan sello | Aceptado |
| [0008](0008-la-aritmetica-es-parte-del-contrato-con-el-rtl.md) | La aritmética es parte del contrato con el RTL (formatos Q, redondeo, tablas exactas) | Aceptado |
| [0009](0009-una-instruccion-cabe-en-tres-columnas-de-bsram.md) | Una instrucción cabe en tres columnas de BSRAM (ISA de 54 bit, 16 instrucciones) | Aceptado |
| [0010](0010-cada-pr-pasa-una-segunda-vuelta-de-optimizacion.md) | Cada PR pasa una segunda vuelta de optimización (timing, listones de recursos y pistas) | Aceptado |
| [0011](0011-el-timing-se-mide-en-la-placa.md) | El timing se mide en la placa, no se cree a nextpnr (margen con el mismo rutado) | Aceptado |
| [0012](0012-los-esquematicos-se-generan-del-rtl.md) | Los esquemáticos se generan del RTL, no se dibujan (Yosys + netlistsvg, PDF) | Aceptado |
