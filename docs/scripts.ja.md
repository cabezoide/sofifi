<!-- i18n: fuente=docs/scripts.md sha=35d6b1ed2f0c estado=al_dia -->
# スクリプトと `sofifi` CLI

このガイドは、`scripts/` の各スクリプトと `sofifi` CLI の各コマンドを説明します。内容は作業ごとにまとめています。各ツールについて、何をするか、典型的なコマンド、必要なもの、どのゲートまたはフェーズで使うかを示します。

詳細は各スクリプトのヘッダーまたは docstring にあります。argparse を使う Python スクリプトと `sofifi` CLI は、`--help` でもヘルプを表示します。

## 始める前に

- すべてのコマンドはリポジトリのルートで実行します。`sofifi` CLI は現在のディレクトリで `programas/` と `presets/` を探します。
- `make install` で環境を一度作ります。モデル、ゲートのツール、EDA ツールチェーンが `.venv` に入ります。
- `make hooks` でフックを一度インストールします。
- ボードを使うには、udev ルール `scripts/udev/99-tang-primer-25k.rules` をインストールします。手順はそのヘッダーにあります。

ほぼすべてのツールに共通の終了コード：

| コード | 意味 |
|---|---|
| 0 | 正常：チェックが通る、または作業が終わる。 |
| 1 | チェックが失敗する、またはボードの結果がモデルと異なる。 |
| 2 | 使い方の誤り：引数が足りない、またはジョブが存在しない。 |

## 1. CI ゲート

ゲートはリポジトリの中にあります（ADR 0001）。ジョブの一覧は `scripts/ci_local.sh` だけです。フック `scripts/hooks/pre-push` はこれを `--no-soft` で呼び、独自の一覧を持ちません。

### `scripts/ci_local.sh` のジョブ

表は `scripts/ci_local.sh` の `JOBS` 一覧の実行順です。クラス名はスクリプト内のスペイン語のままです：`dura`（ハード）、`blanda`（ソフト）、`release`（リリース）。

| ジョブ | クラス | 確認する内容 | スクリプトまたはコマンド |
|---|---|---|---|
| `tech-debt` | ハード | 負債マーカーで始まるコメントがない。 | `scripts/check_tech_debt.sh` |
| `secrets` | ハード | 禁止ファイルや認証情報がない。1 ファイルは 1 MiB まで、デモの `.ogg` は 4 MiB まで。 | `scripts/check_secrets_hygiene.sh` |
| `licenses` | ハード | すべてのソースに SPDX ヘッダーがある。外部のコードは `docs/terceros.yaml` に登録されている（ADR 0002）。 | `scripts/check_licenses.py` |
| `adr-gate` | ハード | `docs/adr/sentinelas.txt` の監視対象を変える diff は、ADR も変える。 | `scripts/check_adr_gate.sh` |
| `docs` | ハード | マップ文書が参照するパス、`make` ターゲット、ADR が存在する。フェーズ、バージョン、フック、台帳も確認する。 | `scripts/check_docs.py` |
| `i18n` | ハード | 各翻訳が存在し、その印が正直である（ADR 0007）。 | `scripts/check_i18n.py` |
| `cierre` | ハード | README とインフォグラフィックがバージョンを示し、キャプチャが最新である。 | `scripts/check_cierre.py` |
| `model` | ハード | モデルのスタイル、書式、型、テスト。 | `ruff check`、`ruff format --check`、`mypy`、`pytest -n auto` |
| `rtl-lint` | ハード | `rtl/top/tops.txt` の各トップと、`rtl/comun/`、`rtl/primitivas/`、`rtl/nucleo/` の各モジュールの lint。 | `verilator --lint-only -Wall -DSIMULACION` |
| `sim` | ハード | cocotb テストベンチがモデルと同じビットを出す（ADR 0003）。 | `pytest sim -n 4` |
| `ratchets` | ハード | `docs/ratchets.yaml` のどの測定値も基準より悪くならない。 | `scripts/check_ratchets.py` |
| `shell-lint` | ソフト | `scripts/*.sh` と `scripts/hooks/*` に shellcheck をかける。 | `shellcheck` |
| `esquematicos` | ソフト | `schematics/` の各 PDF が RTL ソースと一致する（ADR 0012）。 | `scripts/esquematicos.py --comprobar` |
| `optimizacion` | リリース | 各トップが合成でき、タイミングを満たす。ヒントを表示する（ADR 0010）。 | `scripts/check_optimizacion.py` |

クラス：

- **ハード**：失敗すると push を止めます。要約に `ROJO`（赤）と出ます。
- **ソフト**：失敗すると `WARN` と出ますが、push は止めません。ツールがないと、ジョブは `NO CORRIÓ`（実行されず）と出します。これを緑として報告しないでください。
- **リリース**：名前を指定したときだけ実行します。すべてのトップを合成し、約 3 分かかります。

### コマンド

| 作業 | コマンド |
|---|---|
| ハードとソフト | `make ci` |
| ハードのみ（pre-push が実行する内容） | `make ci-dura` |
| ジョブ一覧を見る | `scripts/ci_local.sh --list` |
| 一部のジョブだけ | `scripts/ci_local.sh model docs` |
| モデル | `make test` |
| RTL シミュレーション | `make sim` |
| マップ文書と台帳 | `make docs` |
| PR 前の二巡目の最適化 | `make optimizacion`（ジョブ `optimizacion` と `ratchets`） |

`scripts/ci_local.sh` は所要時間を 1 行 `.ci_timing.log` に追記します。このファイルは git に入りません。

### フックと回避方法

| ツール | 内容 | いつ |
|---|---|---|
| `scripts/install_hooks.sh` | `core.hooksPath = scripts/hooks` を設定する。 | 一度だけ、`make hooks` で。 |
| `scripts/hooks/pre-push` | `scripts/ci_local.sh --no-soft` を実行する。 | 毎回の `git push`。 |

名前付きの回避方法。理由があるときだけ使います：

| 変数またはオプション | 効果 |
|---|---|
| `ADR_GATE_ACK=1` | `adr-gate` が ADR のない diff を受け入れる。「確認した。変わる決定はない」という意味。 |
| `PREPUSH_SKIP=1` または `git push --no-verify` | フックがゲートを実行しない。 |

### 個別のチェック

`check_*` スクリプトにはオプションがありません。引数なしで実行します。`check_i18n.py --sellar` 以外はファイルを書きません。

| スクリプト | 典型的なコマンド |
|---|---|
| `scripts/check_docs.py` | `.venv/bin/python scripts/check_docs.py` |
| `scripts/check_i18n.py` | `.venv/bin/python scripts/check_i18n.py` |
| `scripts/check_i18n.py --sellar` | `.venv/bin/python scripts/check_i18n.py --sellar docs/EXTENDING.en.md`（1 回の呼び出しで 1 ファイル） |
| `scripts/check_cierre.py` | `.venv/bin/python scripts/check_cierre.py` |
| `scripts/check_licenses.py` | `.venv/bin/python scripts/check_licenses.py` |
| `scripts/check_ratchets.py` | `.venv/bin/python scripts/check_ratchets.py`（`model` ジョブの後） |

## 2. 合成とボード

ボードは Sipeed Tang Primer 25K です。EDA ツールチェーンはオープンで、`.venv` にあります：yowasp-yosys、yowasp-nextpnr-himbaechel-gowin、gowin_pack、openFPGALoader。トップとそのソースの唯一の一覧は `rtl/top/tops.txt` です。

> **警告。** UART に全速で送信するトップは、PC が読むのを止めると BL616 ブリッジを止めてしまいます。その場合は USB をつなぎ直す必要があります。新しいトップでは送信量を制限してください（`rtl/AGENTS.md`、`fails.md` の F-02）。

| ツール | 内容 | 典型的なコマンド | 必要なもの |
|---|---|---|---|
| `scripts/fpga.sh synth` | トップを合成、配置、配線、パックする。`build/<top>.fs` と `build/<top>_recursos.json` を出力する。 | `make synth TOP=hil_nucleo` | `.venv` |
| `scripts/fpga.sh prog` | ビットストリームを FPGA の SRAM に書き込む。電源を切ると消える。 | `make prog TOP=hil_nucleo`（先に合成する） | USB 接続のボード |
| `scripts/informe_recursos.py` | nextpnr のレポートを要約する：使用セルと MHz。 | `fpga.sh synth` が呼ぶ。 | nextpnr のレポート |
| `scripts/check_optimizacion.py` | すべてのトップを合成し、タイミングを要求し、`PISTA` ヒントを出す。 | `make optimizacion` | `.venv`。ボードは不要 |
| `scripts/leer_uart.py` | FPGA の UART を読み、指定の文字列を要求する。 | `make uart` | ボード、`/dev/ttyUSB1` |

`scripts/fpga.sh` の変数：

| 変数 | 既定値 | 用途 |
|---|---|---|
| `TOP`（Makefile） | `hola_uart` | `make synth` と `make prog` で使う `rtl/top/tops.txt` のトップ。 |
| `FREQ_MHZ` | 100 | nextpnr のクロック目標（ADR 0005）。 |
| `SEMILLAS_PNR` | `2 3 4` | クロックが収束しないときに nextpnr が試すシード（F-33）。 |
| `SYNTH_OPCIONES` | 空 | `synth_gowin` への追加オプション。 |
| `CST` | `rtl/top/primer25k.cst` | ピン制約ファイル。 |

BL616 デバッガーは 2 つのポートを出します：`/dev/ttyUSB0` が JTAG、`/dev/ttyUSB1` が FPGA の UART で、115 200 ボーです。

## 3. ボード上のテスト（HIL）

ビット精度のモデルが基準です（ADR 0003）。タイミングはボードで測ります（ADR 0011）。これらのツールはトップを書き込み、UART でキャプチャを要求し、モデルと比べます。

| ツール | 内容 | 典型的なコマンド | 終了 |
|---|---|---|---|
| `make hil` | プログラムまたはチェーンの ROM を作り、`hil_programa` を合成して書き込み、`scripts/hil_nucleo.py` を実行する。 | `make hil HIL=marea` | 4 096 サンプルが一致すれば 0 |
| `scripts/hil_nucleo.py` | ボードの 4 096 サンプルと CRC-32 をモデルと比べる。`--traza K0` を付けると、最初に食い違う命令を探す。 | `.venv/bin/python scripts/hil_nucleo.py --programa plate` | すべて一致すれば 0 |
| `scripts/hil_lote.py` | 複数の名前について `make hil` を実行し、build/hil_lote.csv に書く。1 つの名前に約 4 分かかる。 | `.venv/bin/python scripts/hil_lote.py --todos` | すべて一致すれば 0 |
| `scripts/margen_reloj.py` | 配線済みの設計の PLL 分周だけを変え、各周波数でキャプチャを繰り返す。 | `.venv/bin/python scripts/margen_reloj.py --divisores 8 7 6` | 100 MHz が常に通れば 0 |
| `scripts/verificar_primitivas.py` | プリミティブのテスト用トップを確認する：`dsp`、`bsram`、`pll`、`fs`。 | `.venv/bin/python scripts/verificar_primitivas.py dsp` | すべての行が正しければ 0 |

各テストが書き込むトップ：

| テスト | トップ | スクリプト |
|---|---|---|
| `plate` を動かすコア | `make prog TOP=hil_nucleo` | `scripts/hil_nucleo.py` |
| ルーパー | `make prog TOP=hil_looper` | `scripts/hil_nucleo.py --programa looper` |
| 任意のプログラムまたはチェーン | `make hil HIL=NOMBRE` | `scripts/hil_nucleo.py --programa NOMBRE`（`make hil` が呼ぶ） |
| クロックの余裕 | `make synth TOP=hil_nucleo` と `make synth TOP=prueba_pll` | `scripts/margen_reloj.py`（ルーパーは `--base hil_looper --programa looper`） |
| DSP 乗算器 | `make prog TOP=prueba_dsp` | `scripts/verificar_primitivas.py dsp` |
| BSRAM | `make prog TOP=prueba_bsram` | `scripts/verificar_primitivas.py bsram` |
| PLL | `make prog TOP=prueba_pll` | `scripts/verificar_primitivas.py pll` |
| サンプリング周波数と UART RX | `make prog TOP=prueba_fs` | `scripts/verificar_primitivas.py fs` |
| microSD | `make prog TOP=prueba_sd` | `scripts/prueba_sd.py`（第 4 節） |

注記：

- `make hil` は `hil_nucleo` のメモリに収まるプログラムまたはチェーンを受け付けます：38 912 ワード。それ以外は `sofifi rom` が拒否します。
- `scripts/margen_reloj.py` には `build/<base>.pnr.json` と build/prueba_pll.fs が必要です。最後に `prueba_pll` を書き込みます。このトップは UART にほとんど送信しません。
- これらのツールは既定で `/dev/ttyUSB1` を読みます。ポートは `--puerto` で変えます。

## 4. microSD

microSD はプログラムを保存します。音声の遅延には使いません（ADR 0004）。`dd` に関する警告を含む手順全体は [microsd.md](microsd.md)（スペイン語のみ）にあります。

| ツール | 内容 | 典型的なコマンド | 必要なもの |
|---|---|---|---|
| `sofifi banco` | バンクのイメージを書く。名前を指定しなければ、収まるものをすべて入れる。 | `.venv/bin/sofifi banco build/banco.img` | なし |
| `sofifi banco --leer` | 各スロットの CRC と制限を確認し、一覧を出す。 | `.venv/bin/sofifi banco --leer build/banco.img` | なし |
| `scripts/prueba_sd.py` | `prueba_sd` に各スロットを読み込ませ、モデルと比べる。 | `.venv/bin/python scripts/prueba_sd.py --imagen build/banco.img` | ボード、J6 の PMOD TF、書き込み済みのカード、`/dev/ttyUSB1` |

フェーズ 08：`scripts/prueba_sd.py` はまだ実際のカードで試していません。

## 5. ドキュメントとメディア

| ツール | 内容 | 典型的なコマンド | いつ |
|---|---|---|---|
| `scripts/check_i18n.py --sellar` | 翻訳の印を最新にする。 | `.venv/bin/python scripts/check_i18n.py --sellar README.en.md` | 翻訳を更新するたびに（ADR 0007）。 |
| `scripts/capturar_infografia.py` | インフォグラフィックの各節を PNG に撮り、そのハッシュを `docs/img/capturas.json` に記録する。 | `.venv/bin/python scripts/capturar_infografia.py --todas` | フェーズを閉じるとき（ゲート `cierre`）。 |
| `scripts/esquematicos.py` | `schematics/` に RTL モジュールごとの PDF を作る。 | `make esquematicos` | RTL モジュールを変えた後（ADR 0012）。 |
| `scripts/generar_demos.py` | `demo_examples/` の Ogg デモと説明を作り直す。 | `.venv/bin/python scripts/generar_demos.py` | デモのあるプログラムを変えた後。 |
| `sofifi catalogo` | プログラム、プリセット、チェーンのカタログを作り直す。 | `.venv/bin/sofifi catalogo` | プログラム、プリセット、チェーンを変えた後。 |

必要なもの：

- `scripts/capturar_infografia.py` と `scripts/esquematicos.py` には、Playwright のキャッシュにある chrome-headless-shell（`~/.cache/ms-playwright`）が必要です。
- `scripts/esquematicos.py` には netlistsvg も必要です：`make esquematicos` は先に `herramientas/esquematicos/` で `npm install` を実行します。`--comprobar` オプションはどちらも使いません。
- `scripts/generar_demos.py` には `demos` エクストラが必要です（`make install` が入れます）。8 コアで約 2 分かかります。音声が変わったときだけ `.ogg` を書き直します。

## 6. モデルとプログラム：`sofifi` CLI

`sofifi` CLI はビット精度モデルの入口です。`make install` が `.venv/bin/sofifi` に入れます。各コマンドは `sofifi コマンド --help` でヘルプを表示します。

| コマンド | 内容 | 例 | 書き込むもの |
|---|---|---|---|
| `asm` | プログラムをアセンブルし、2 048 RTL サイクルのうち使うサイクル数を示す（ADR 0005）。 | `sofifi asm programas/plate.sasm build/plate` | build/plate.hex と build/plate.json |
| `tablas` | Hermite テーブルと RTL の ROM プログラムを作り直す。 | `sofifi tablas` | `rtl/` の `.v` ファイル |
| `catalogo` | プログラム、プリセット、チェーンのカタログを作り直す。 | `sofifi catalogo` | `docs/programas.md` とその翻訳 |
| `render` | プログラムで WAV ファイルを処理する。 | `sofifi render programas/plate.sasm seca.wav plate.wav --preset 'Placa corta'` | 出力 WAV |
| `presets` | `presets/banco.toml` のプリセットを一覧する。 | `sofifi presets plate` | なし |
| `cadenas` | チェーンをコストとともに一覧し、収まるかを示す（ADR 0013）。 | `sofifi cadenas` | なし |
| `componer` | チェーンを 1 つのプログラムとして書く。 | `sofifi componer "Eco y muelle" build/eco.sasm` | 出力 `.sasm` |
| `cadena` | チェーンで WAV ファイルを処理する。 | `sofifi cadena "Eco y muelle" seca.wav eco.wav` | 出力 WAV |
| `rom` | プログラムまたはチェーンの `programa_hil` ROM を書く。 | `sofifi rom marea build/programa_hil.v` | 出力 `.v` |
| `banco` | microSD のイメージを書く、または確認する。 | `sofifi banco build/banco.img` | イメージ |

`render` と `cadena` のオプション：

| オプション | 効果 |
|---|---|
| `--pot potN=V` | ノブ N を値 V（0 から 1）にする。繰り返し指定できる。 |
| `--freeze INICIO:FIN` | この秒数の間フットスイッチを押す。繰り返し指定できる。 |
| `--cola S` | 最後に S 秒の無音を加える。 |
| `--preset NOMBRE` | `render` のみ：プリセットのノブ値から始め、その後に各 `--pot` を適用する。 |

チェーンは `presets/cadenas.toml` のノブ位置から始まります。

プログラム、RTL モジュール、ゲートを追加するには [EXTENDING.ja.md](EXTENDING.ja.md) を読んでください。

### コアの受け入れテスト

`sim/nucleo/nucleo_test.py` は RTL のコアをモデルと比べます。ゲート `sim` は 1 000 サンプルを使います。完全な受け入れテスト：

```sh
SOFIFI_MUESTRAS=4883 .venv/bin/python -m pytest sim/nucleo/nucleo_test.py
```

## 知っておくべき動作

- `scripts/generar_demos.py` は `--readme`、`--help`、または引数なしを受け付けます。それ以外の引数では終了コード 2 を返し、デモを作りません。
- `check_*` スクリプトは引数を読みません。`scripts/check_optimizacion.py --help` はすべてのトップを合成します。
- `scripts/informe_recursos.py` には nextpnr レポートのパスが必要です。ないと使い方を表示し、終了コード 2 を返します。
- 引数が正しくないとき、または chrome-headless-shell がないとき、`scripts/capturar_infografia.py` はヘルプを表示して 1 で終了します。
- `scripts/ci_local.sh --help` と、コマンドなしの `scripts/fpga.sh` はヘッダーを表示します。
