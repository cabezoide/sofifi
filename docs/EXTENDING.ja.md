<!-- i18n: fuente=docs/EXTENDING.md sha=3bfc3280c871 estado=al_dia -->
# 拡張の方法

部品の種類ごとの手順です。何かを追加するときにこのリストにない箇所を変更する必要があれば、リストが不完全です。同じ PR で修正してください。

## プログラム（エフェクト）

エフェクトはプログラムであり、RTL モジュールではありません（ADR 0006（スペイン語））。

1. 第三者由来のプログラムの場合は、`docs/terceros.yaml` にエントリーを追加してください。
   `uso: portado` は寛容型ライセンスの場合だけ使えます（ADR 0002（スペイン語））。
2. `programas/<nombre>.sasm` を書いてください。ヘッダーには次の行を入れます。
   - `; familia:` と `; resumen:`。
   - `; resumen.en:`、`; resumen.zh-CN:`、`; resumen.ja:`。翻訳した要約です。
   - `; potN = nombre`。ノブごとに 1 行です。
3. 既存のブロックは `include` で `programas/comun/` から取り込んでください。
4. 収まることを確認してください。`sofifi asm programas/<nombre>.sasm out/<nombre>` が
   RTL のサイクル数を出します。2,048 以下でなければなりません（`model/sofifi/domain/coste.py`）。
5. その音響特性のテストを `model/tests/` に書いてください。所属ファミリーのファイルか、専用のファイルに書きます。共通の測定は `model/tests/acustica.py` にあります。
6. `HUELLAS`（`model/tests/programas_test.py`）にフィンガープリントを追加してください。「収まる」、フィンガープリント、RTL との一致（`sim/nucleo/nucleo_test.py`）のテストは
   すべての `.sasm` を走査します。何かが欠けていれば失敗します。
7. ノブに新しい名前がある場合は、`MANDOS`（`model/sofifi/services/catalogo_textos.py`）に
   その翻訳を追加してください。`model/tests/catalogo_test.py` がこれを求めます。
8. プリセットを 5 個以上追加してください（「プリセット」の節）。
9. `sofifi catalogo` で、カタログを 4 言語で再生成してください。
10. `DEMOS`（`scripts/generar_demos.py`）にデモを追加してください。スクリプトを実行します。
    スクリプトは `.ogg` とガイド `demo_examples/README*.md` を書きます。
11. プログラムが `hil_nucleo` の 38 ブロックに収まる場合は、`make hil HIL=<nombre>` で
    ボード上で試験してください。

## 既存のプログラムの変更

> **警告。** `programas/comun/` を変更すると、それを取り込むすべてのプログラムが変わります。
> F-32 は 74 のプログラムのフィンガープリントを変えました。

1. `HUELLAS` の中で、変わるフィンガープリントを更新してください。
2. `plate`、`looper`、またはそれらが取り込むブロックが変わる場合は、`sofifi tablas` を実行してください。
   ROM `rtl/top/programa_plate.v` と `rtl/top/programa_looper.v` を再生成します。
   `model/tests/tablas_test.py` がこれを求めます。
3. `sofifi catalogo` でカタログを再生成してください。
4. `scripts/generar_demos.py` でデモを再生成してください。`.ogg` は、その音声が
   変わったときだけ書き直されます。

## プリセット

プリセットは、同じプログラムに別のノブの値と名前を付けたものです。

1. `presets/banco.toml` のプログラムのテーブルに、`"Nombre" = [pot0, pot1, …]` の行を
   1 行追加してください。値は 0 から 1 までです。使わないノブは 0 にします。
2. プリセットを聴いてください：`sofifi render programas/<programa>.sasm entrada.wav salida.wav --preset "Nombre"`。
3. `sofifi catalogo` でカタログを再生成してください：カタログはプリセットの数を数えます。
   `model/tests/presets_test.py` がプログラム、ノブ、範囲を確認します。

## チェーン（2 つのプログラムを 1 つに）

チェーンは既存のプログラムをつなぎます。RTL は変わりません（ADR 0013（スペイン語））。

1. `sofifi cadenas` で、似たチェーンがどれだけ使うかを確かめてください。各プログラムは
   自分のレジスタと LFO を使います。コアには汎用レジスタが 32 個、LFO が 4 つあります。
2. `presets/cadenas.toml` に `[[cadena]]` を追加してください。
   - `mandos` では、数値は固定値、`"potN"` はペダルの N 番目のポットです。
   - `pots` は、チェーンを読み込んだときの 6 つのポットの位置です。
3. チェーンに足りないのがメモリーだけの場合は、`requiere = "sdram"` としてください。
   `model/tests/cadenas_test.py` は、各チェーンが収まるか、足りないのがメモリーだけであることを求めます。
4. `sofifi cadena NOMBRE entrada.wav salida.wav` で聴いてください。チェーンが plate の
   2 倍を超える音量なら、音量のテストが失敗します。
5. 合成プログラムを見るには、`sofifi componer NOMBRE salida.sasm` を実行してください。
6. `sofifi catalogo` でカタログを再生成してください。RTL シミュレーションは
   収まるチェーンを実行します。
7. デモを作るには、`DEMOS_CADENAS`（`scripts/generar_demos.py`）にチェーンを追加してください。
8. チェーンが `hil_nucleo` に収まる場合は、`make hil HIL="NOMBRE"` でボード上で試験してください。

## コアの命令

新しい命令は構造上の決定です。`model/sofifi/domain/isa.py` はセンチネルです：
変更にはその ADR か、ADR 0009（スペイン語）の更新を伴います。

1. `Op` に値を追加してください。1 サイクルより多くかかる場合は、`CICLOS`（`model/sofifi/domain/isa.py`）にも追加します。
2. `model/sofifi/domain/nucleo.py` にハンドラーを書き、`MANEJADORES` に登録してください。
3. `model/sofifi/domain/ensamblador.py` にニーモニックとオペランドを追加してください。
   3 つの手順のどれかが欠けていれば、`model/tests/nucleo_test.py` と `model/tests/ensamblador_test.py`
   の契約テストが失敗します。
4. 実行サイクルを `DURACION`（`model/sofifi/domain/coste.py`）に追加してください。
5. 命令が ACC かレジスタバンクを読む場合は、`LEE_ACC` か `LEE_REGISTRO` にも追加してください。
6. `MUESTRA_COSTE`（`sim/nucleo/nucleo_test.py`）に 1 行追加してください。シミュレーションは、
   単独でも各命令の隣でも、タイミングモデルと同じサイクル数を求めます（ADR 0014（スペイン語））。

## RTL モジュール

1. まずモデルを `model/sofifi/domain/` に書いてください。
2. SPDX ヘッダー付きで、RTL を `rtl/` に書いてください。
3. テストベンチを `sim/` に書いてください。テストベンチはサンプルごとにモデルと比較します。
4. モジュールがピン、クロック、メモリーマップを固定する場合は、同じ PR でその ADR を書いてください。
   これらのファイルはセンチネルです（`docs/adr/sentinelas.txt`）。
5. `make esquematicos` で回路図を再生成してください（ADR 0012（スペイン語））。
6. `docs/arquitectura_fpga.md` と `SBOM.md` を、その翻訳と一緒に更新してください。

## トップ

トップは、ボード用の完全な設計です：ピン、PLL、モジュールを含みます。

1. `rtl/top/<top>.v` を書いてください。ピンは `rtl/top/primer25k.cst` にあります。
2. `rtl/top/tops.txt` に、トップとそのソースの行を 1 行追加してください。最初のソースが
   トップを定義します。Makefile とゲートはこのリストを読みます。
3. `docs/ratchets.yaml` に、ラチェット `recursos:<top>:LUT4` と `recursos:<top>:ALU` を
   現在の値で追加してください（ADR 0010（スペイン語））。
4. `make prog TOP=<top>` で合成し、書き込んでください。
5. トップが UART で送信する場合は、送信量を制限してください：制限しないと BL616 のブリッジが
   止まります（`rtl/AGENTS.md`（スペイン語））。
6. クロックのマージンは nextpnr ではなく、ボード上で測ってください（ADR 0011（スペイン語））。

## ゲート

> **警告。** `scripts/ci_local.sh` はセンチネルです：その変更には、その ADR か
> ADR の更新を伴います。

1. `scripts/` にスクリプトを追加してください。
2. `scripts/ci_local.sh` の `JOBS` 配列に `"nombre:dura|blanda|release"` の行を 1 行追加し、
   `run_job` にその分岐を追加してください。フックは変更しません。
3. クラスを宣言してください。
   - ハード：全員が今日実行して修正できる場合だけ（P1）。
   - release：コストが高く、名前を指定したときだけ実行する場合（`make release-check`、`make optimizacion`）。
   - ソフト：それ以外の場合。
4. ゲートが EDA ツールを起動する場合は、`(ulimit -u "$TOPE_PROCESOS"; …)` の中に入れてください。

## ADR

1. `docs/adr/0001-la-compuerta-vive-en-el-repositorio.md`（スペイン語）の構成をもとに、
   `docs/adr/<NNNN>-<regla-en-kebab>.md` を作成してください。
2. 索引 `docs/adr/README.md`（スペイン語）に行を追加してください。`docs` ゲートが
   両者の一致を確認します。

## フェーズ

1. `docs/fases/` に、固定のセクションを持つ仕様を書いてください（SPEC_RAIZ §2.5（スペイン語））。
2. フェーズを閉じるまで、管理対象に追加**しない**でください。
3. 閉じるときは、`docs/fases/estado_fases.csv` に、発見事項と修正を記した行を追加してください。
4. 4 つの README のバージョンを `0.<fase>` に上げてください。
5. 同じ PR で、すべてのドキュメントとインフォグラフィックを 4 言語で更新してください。
   `scripts/capturar_infografia.py --todas` でキャプチャを作り直します。
   `cierre` ゲートがこれを確認します。
