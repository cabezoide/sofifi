<!-- i18n: fuente=docs/EXTENDING.md sha=3b5545c20179 estado=al_dia -->
# 拡張の方法

部品の種類ごとの手順です。何かを追加するときにこのリストにない箇所を変更する必要があれば、リストが不完全です。同じ PR で修正してください。

## エフェクト（コアのプログラム）

エフェクトはプログラムであり、RTL モジュールではありません（ADR 0006（スペイン語））。

1. 第三者由来の場合は、`docs/terceros.yaml` にエントリーを追加してください。`uso: portado` は寛容型ライセンスの場合だけ使えます（ADR 0002（スペイン語））。
2. `programas/<nombre>.sasm` を書いてください。ヘッダーには `; familia:`、
   `; resumen:` と、ノブごとに 1 行の `; potN = nombre` を入れます。既存のブロックは `include` で `programas/comun/` から取り込みます。
3. 収まることを確認してください。`sofifi asm` が RTL のサイクル数を出します。2,048 以下でなければなりません（`model/sofifi/domain/coste.py`）。
4. その音響特性のテストを、所属ファミリーのファイル（`model/tests/programas_<familia>_test.py`）に書いてください。共通の測定は `model/tests/acustica.py` にあります。
5. `HUELLAS`（`model/tests/programas_test.py`）にフィンガープリントを追加してください。「収まる」、フィンガープリント、RTL との一致（`sim/nucleo/nucleo_test.py`）のテストはすべての `.sasm` を走査します。何かが欠けていれば失敗します。
6. `presets/banco.toml` に、プログラム名のテーブルでプリセットを 5 個以上追加してください。`model/tests/presets_test.py` がノブを確認します。
7. `sofifi catalogo` でカタログを再生成してください。
8. `DEMOS`（`scripts/generar_demos.py`）と `demo_examples/README.ja.md` にデモを追加してください。

## チェーン（2 つのプログラムを 1 つに）

チェーンは既存のプログラムをつなぎます。RTL は不要です（ADR 0013、スペイン語）。

1. `sofifi cadenas` で、似たチェーンがどれだけ使うかを確かめる。各プログラムは自分のレジスタと LFO を使う。コアには 32 のレジスタと 4 つの LFO がある。
2. `presets/cadenas.toml` に `[[cadena]]` を追加する。`mandos` では、数値は固定値、`"potN"` はペダルの N 番目のポット。`pots` はチェーンを読み込んだときの 6 つのポットの位置。
3. メモリーだけが足りない場合は `requiere = "sdram"` とする。`model/tests/cadenas_test.py` は、各チェーンが収まるか、足りないのがメモリーだけであることを求める。
4. `sofifi cadena 名前 入力.wav 出力.wav` で聴く。チェーンが plate の 2 倍を超える音量なら、音量のテストが失敗する。
5. `sofifi catalogo` でカタログを再生成する。RTL シミュレーションは収まるチェーンを実行する。

## コアの命令

これは構造上の決定です。`model/sofifi/domain/isa.py` はセンチネルなので、その ADR か ADR 0009（スペイン語）の更新を伴います。

1. `Op` に値を追加してください。1 サイクルより多くかかる場合は、`CICLOS`（`model/sofifi/domain/isa.py`）にも追加します。
2. `model/sofifi/domain/nucleo.py` にハンドラーを書き、`MANEJADORES` に登録してください。
3. `model/sofifi/domain/ensamblador.py` にニーモニックとオペランドを追加してください。
4. 3 つの手順のどれかが欠けていれば、`model/tests/nucleo_test.py` と `model/tests/ensamblador_test.py` の契約テストが失敗します。
5. RTL のサイクルコストを `CICLOS_RTL`（`model/sofifi/domain/coste.py`）に追加し、`MUESTRA_COSTE`（`sim/nucleo/nucleo_test.py`）に 1 行追加してください。シミュレーションがコストを測定し、表と比較します。

## RTL モジュール

1. まずモデルを `model/sofifi/domain/` に書いてください。
2. RTL は SPDX ヘッダー付きで `rtl/` に置きます。
3. テストベンチは `sim/` に置き、サンプルごとに比較します。
4. トップの場合は、ソースとともに `rtl/top/tops.txt` に登録してください。`docs/ratchets.yaml` に `recursos:<top>:LUT4` と `recursos:<top>:ALU` のラチェットを、現在の値で設定します（ADR 0010（スペイン語））。
5. ピン、クロック、メモリーマップを固定する場合は、その ADR を伴います。これらのファイルはセンチネルです（`docs/adr/sentinelas.txt`）。
6. `make esquematicos` で回路図を再生成してください（ADR 0012（スペイン語））。

## ゲート

1. `scripts/` にスクリプトを追加してください。`scripts/ci_local.sh` の `JOBS` 配列に `"nombre:dura|blanda|release"` の行を 1 行追加し、`run_job` にその分岐を追加します。フックは変更しません。
2. クラスを宣言してください。全員が今日実行して修正できる場合だけハードにします（P1）。コストが高く、名前を指定したときだけ実行するなら release にします（`make release-check`、`make optimizacion`）。
3. EDA ツールを起動する場合は、`(ulimit -u "$TOPE_PROCESOS"; …)` の中に入れてください。
4. `scripts/ci_local.sh` の変更はセンチネルに触れるので、その ADR か ADR の更新を伴います。

## ADR

1. `docs/adr/0001-la-compuerta-vive-en-el-repositorio.md`（スペイン語）の構成をもとに、`docs/adr/<NNNN>-<regla-en-kebab>.md` を作成してください。
2. 索引 `docs/adr/README.md`（スペイン語）に行を追加してください。`docs` ゲートが両者の一致を確認します。

## フェーズ

1. `docs/fases/` に、固定のセクションを持つ仕様を書いてください（SPEC_RAIZ §2.5（スペイン語））。
2. フェーズを閉じるまで、管理対象に追加**しない**でください。閉じるときは、`docs/fases/estado_fases.csv` に発見事項と修正を記した行を追加し、README のバージョンを `0.<fase>` に上げます。
3. 同じ PR で、すべてのドキュメントとインフォグラフィックを 4 言語で更新します。`scripts/capturar_infografia.py --todas` でキャプチャを作り直します。`cierre` ゲートがこれを確認します。
