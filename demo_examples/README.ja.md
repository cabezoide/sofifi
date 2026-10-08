<!-- i18n: fuente=demo_examples/README.md sha=5fc2eee58a60 estado=al_dia -->
# demo_examples

合成ギター（Em9 のアルペジオ、Karplus-Strong の弦）を、ビット精度のモデルでコアの各プログラムに通したものです。`.venv/bin/python scripts/generar_demos.py` で再生成でき、毎回同じ音声になります。

| ファイル | プログラム | ノブ | フットスイッチ |
|---|---|---|---|
| `demo_guitarra.ogg` | — | — | — |
| `demo_plate.ogg` | `plate` | ディケイ 0.70 · ダンピング 0.30 · ミックス 0.45 | — |
| `demo_shimmer.ogg` | `shimmer` | ディケイ 0.75 · ダンピング 0.25 · ミックス 0.55 · シマー量 0.60 | — |
| `demo_freeze.ogg` | `freeze` | ディケイ 0.60 · ダンピング 0.30 · ミックス 0.50 | 2.50 → 8.00 s |
| `demo_hall.ogg` | `hall` | ディケイ 0.75 · ダンピング 0.35 · ミックス 0.45 | — |
| `demo_cloud.ogg` | `cloud` | ディケイ 0.70 · ダンピング 0.30 · ミックス 0.55 · モジュレーション 0.60 | — |
| `demo_cinta.ogg` | `cinta` | タイム 0.45 · フィードバック 0.55 · ミックス 0.40 · ワウとフラッター 0.50 | — |
| `demo_reverse.ogg` | `reverse` | トーン 0.60 · フィードバック 0.40 · ミックス 0.50 | — |
| `demo_lofi.ogg` | `lofi` | サンプリング周波数 0.60 · ビット 0.70 · ミックス 0.70 · トーン 0.40 | — |
| `demo_swell.ogg` | `swell` | ディケイ 0.70 · ダンピング 0.30 · ミックス 0.50 · 立ち上がり 0.40 | — |
| `demo_chorus.ogg` | `chorus` | 速さ 0.30 · 深さ 0.60 · ミックス 0.50 | — |
| `demo_flanger.ogg` | `flanger` | 速さ 0.15 · 深さ 0.80 · ミックス 0.50 · フィードバック 0.60 | — |
| `demo_phaser.ogg` | `phaser` | 速さ 0.20 · 深さ 0.90 · ミックス 0.50 · フィードバック 0.50 | — |
| `demo_tremolo.ogg` | `tremolo` | 速さ 0.30 · 深さ 0.70 · パン 0.60 | — |
| `demo_vibrato.ogg` | `vibrato` | 速さ 0.40 · 深さ 0.50 · ミックス 1.00 | — |
| `demo_octava.ogg` | `octava` | 下のオクターブ 0.60 · 上のオクターブ 0.40 · ドライ 0.80 | — |
| `demo_armonizador.ogg` | `armonizador` | 音程 0.75 · フィードバック 0.30 · ミックス 0.45 | — |
| `demo_doblador.ogg` | `doblador` | デチューン 0.50 · ミックス 0.50 | — |
| `demo_escalera.ogg` | `escalera` | 音程 0.95 · フィードバック 0.60 · ミックス 0.45 · タイム 0.40 | — |
| `demo_shimmer_quinta.ogg` | `shimmer_quinta` | ディケイ 0.75 · ダンピング 0.25 · ミックス 0.55 · シマー量 0.60 | — |
| `demo_blackhole.ogg` | `blackhole` | ディケイ 0.85 · ダンピング 0.35 · ミックス 0.50 | — |
| `demo_bloom.ogg` | `bloom` | ディケイ 0.80 · ダンピング 0.30 · ミックス 0.55 · 開く時間 0.40 | — |
| `demo_gated.ogg` | `gated` | ディケイ 0.80 · ダンピング 0.20 · ミックス 0.50 · 長さ 0.50 | — |
| `demo_infinite.ogg` | `infinite` | リリース 0.10 · ダンピング 0.30 · ミックス 0.45 | — |
| `demo_reverb_inversa.ogg` | `reverb_inversa` | ディケイ 0.80 · ダンピング 0.30 · ミックス 0.55 · 長さ 0.60 | — |
| `demo_spring.ogg` | `spring` | ディケイ 0.60 · ダンピング 0.40 · ミックス 0.40 | — |
| `demo_delay.ogg` | `delay` | タイム 0.55 · フィードバック 0.45 · ミックス 0.40 · トーン 0.70 | — |
| `demo_pingpong.ogg` | `pingpong` | タイム 0.70 · フィードバック 0.50 · ミックス 0.45 | — |
| `demo_lluvia.ogg` | `lluvia` | 拡散 0.70 · フィードバック 0.40 · ミックス 0.50 | — |
| `demo_bbd.ogg` | `bbd` | タイム 0.60 · フィードバック 0.60 · ミックス 0.45 · モジュレーション 0.50 | — |
| `demo_ducking.ogg` | `ducking` | タイム 0.45 · フィードバック 0.50 · ミックス 0.50 · ダッキング 0.80 | — |
| `demo_autowah.ogg` | `autowah` | 感度 0.80 · レゾナンス 0.60 · ミックス 0.80 | — |
| `demo_compresor.ogg` | `compresor` | スレッショルド 0.30 · 圧縮 0.80 · ミックス 1.00 · ゲイン 0.40 | — |
| `demo_filtro.ogg` | `filtro` | 速さ 0.25 · レゾナンス 0.60 · ミックス 0.90 · 深さ 0.80 | — |
| `demo_puerta.ogg` | `puerta` | スレッショルド 0.20 · リリース 0.40 | — |
| `demo_saturacion.ogg` | `saturacion` | ゲイン 0.60 · トーン 0.50 · ミックス 1.00 · レベル 0.70 | — |
| `demo_ringmod.ogg` | `ringmod` | 周波数 0.15 · ミックス 0.60 | — |
| `demo_slicer.ogg` | `slicer` | 速さ 0.30 · 深さ 0.90 · デューティ比 0.40 · スムージング 0.40 | — |
| `demo_ancho.ogg` | `ancho` | 幅 0.80 · チルト 0.60 | — |
| `demo_chorale.ogg` | `chorale` | ディケイ 0.75 · ダンピング 0.30 · ミックス 0.55 · 母音 0.30 | — |
| `demo_resonador.ogg` | `resonador` | サステイン 0.80 · 励起 0.70 · ミックス 0.50 | — |
| `demo_plate_vivo.ogg` | `plate_vivo` | ディケイ 0.75 · ダンピング 0.30 · ミックス 0.45 · ゆらぎ 1.00 | — |
| `demo_shimmer_energia.ogg` | `shimmer_energia` | ディケイ 0.80 · ダンピング 0.25 · ミックス 0.55 · シマー量 0.90 | — |
| `demo_freeze_givens.ogg` | `freeze_givens` | ディケイ 0.60 · ダンピング 0.30 · ミックス 0.50 · 回転 0.60 | 2.50 → 8.00 s |
| `demo_looper.ogg` | `looper` | レベル 0.80 · 速さ 0.50 · 方向 0.00 · フィードバック 0.80 | 0.00 → 0.66 s, 1.32 → 1.98 s |

Ogg Vorbis、48,828 Hz（ADR 0005、スペイン語）。レンダリングは 24 ビットでビット精度です。ノブとプログラムは `docs/programas.ja.md` にあります。
