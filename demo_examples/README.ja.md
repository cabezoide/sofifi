<!-- i18n: fuente=demo_examples/README.md sha=01075f5aa939 estado=al_dia -->
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
| `demo_granular.ogg` | `granular` | 長さ 0.60 · 拡散 0.50 · 音程 1.00 · ミックス 0.60 | 1.60 → 7.00 s |
| `demo_shimmer_grave.ogg` | `shimmer_grave` | ディケイ 0.75 · ダンピング 0.30 · ミックス 0.50 · シマー量 0.60 | — |
| `demo_marea.ogg` | `marea` | ディケイ 0.80 · ダンピング 0.30 · ミックス 0.50 · 速さ 0.20 | — |
| `demo_ensemble.ogg` | `ensemble` | ディケイ 0.75 · ダンピング 0.30 · ミックス 0.50 · アンサンブル 0.70 | — |
| `demo_sostenido.ogg` | `sostenido` | レイヤー 0.20 · ダンピング 0.30 · ミックス 0.50 · キャプチャー 0.30 | — |
| `demo_shoegaze.ogg` | `shoegaze` | ディケイ 0.85 · ダンピング 0.30 · ミックス 0.55 · サチュレーション 0.80 | — |
| `demo_bruma.ogg` | `bruma` | 拡散 0.70 · フィードバック 0.55 · ミックス 0.50 · ヘッド 1.00 | — |
| `demo_armonico.ogg` | `armonico` | 速さ 0.30 · 深さ 0.75 · エコー 0.35 · 周波数 0.50 · 波形 0.10 · 幅 0.80 | — |
| `demo_arcoiris.ogg` | `arcoiris` | 音程 0.79 · 第2声部 0.00 · ミックス 0.50 · タイム 0.30 · フィードバック 0.75 · トーン 0.60 | 2.50 → 4.00 s |
| `demo_tambor.ogg` | `tambor` | 速さ 0.55 · フィードバック 0.50 · ミックス 0.45 · ヘッド 0.85 · エイジング 0.40 · トーン 0.60 | 3.50 → 5.00 s |
| `demo_mosaico.ogg` | `mosaico` | 下のオクターブ 0.60 · レベル 0.70 · ミックス 0.55 · 上のオクターブ 0.50 · フィードバック 0.85 · 拡散 0.60 | 4.00 → 8.00 s |
| `demo_erosion.ogg` | `erosion` | 侵食 0.25 · ダンピング 0.60 · ミックス 0.65 · モジュレーション 0.70 · レベル 1.00 · 長さ 1.00 | 0.00 → 0.67 s |
| `demo_desplazador.ogg` | `desplazador` | 周波数シフト 0.75 · タイム 0.45 · ミックス 0.50 · フィードバック 0.85 · トーン 0.70 · 幅 0.50 | — |
| `demo_violin.ogg` | `violin` | 立ち上がり 0.50 · タイム 0.30 · ミックス 1.00 · 深さ 0.60 · 速さ 0.30 · トーン 0.50 | — |
| `demo_shimmer_escondido.ogg` | `shimmer_escondido` | ディケイ 0.80 · ダンピング 0.25 · ミックス 0.55 · シマー量 0.80 · ダッキング 1.00 · トーン 0.40 | — |
| `demo_arco.ogg` | `arco` | サステイン 0.85 · 立ち上がり 0.50 · ミックス 0.85 · 上のオクターブ 0.70 · トーン 0.30 · スレッショルド 0.20 | — |
| `demo_oscilador.ogg` | `oscilador` | タイム 0.12 · フィードバック 0.70 · ミックス 0.50 · スムージング 0.70 · トーン 0.40 · レベル 0.20 | 2.00 → 4.00 s |
| `demo_dinamica.ogg` | `dinamica` | ディケイ 0.75 · ダンピング 0.30 · ミックス 0.45 · 深さ 0.85 · スレッショルド 0.10 · 速さ 0.10 | — |
| `demo_acople.ogg` | `acople` | タイム 0.00 · 音程 0.00 · ミックス 1.00 · 立ち上がり 0.15 · トーン 0.55 · レベル 1.00 | — |
| `demo_enjambre.ogg` | `enjambre` | 広がり 0.40 · フィードバック 0.70 · ミックス 0.50 · 拡散 0.60 · トーン 0.60 · ドリフト 0.40 | 2.00 → 4.00 s |
| `demo_probabilidad.ogg` | `probabilidad` | タイム 0.75 · 確率 0.50 · ミックス 0.45 · フィードバック 0.60 · トーン 0.70 · スムージング 0.40 | 3.00 → 5.00 s |
| `demo_dados.ogg` | `dados` | タイム 0.70 · フィードバック 0.60 · ミックス 0.50 · 確率 0.40 · トーン 0.60 · 幅 0.70 | 1.50 → 1.60 s, 3.00 → 3.10 s |
| `demo_aureo.ogg` | `aureo` | 傾き 0.60 · フィードバック 0.60 · ミックス 0.45 · トーン 0.60 · 幅 0.90 · 拡散 0.40 | 2.50 → 5.00 s |
| `demo_estelar.ogg` | `estelar` | タイム 0.45 · フィードバック 0.75 · ミックス 0.45 · 深さ 0.90 · 速さ 0.25 · レゾナンス 0.40 | — |
| `demo_lata.ogg` | `lata` | タイム 0.35 · フィードバック 0.55 · ミックス 0.45 · 深さ 0.60 · トーン 0.40 · オイル 0.50 | 3.00 → 3.60 s |
| `demo_deriva.ogg` | `deriva` | タイム 0.45 · 深さ 0.50 · ミックス 0.45 · 速さ 0.35 · グライド 0.40 · フィードバック 0.50 | — |
| `demo_dimension.ogg` | `dimension` | モード 0.65 · 速さ 0.50 · ミックス 0.50 · 深さ 0.60 · クロスフィード 0.90 · トーン 0.70 | — |
| `demo_vibe.ogg` | `vibe` | 速さ 0.25 · 深さ 0.80 · ミックス 0.00 · フィードバック 0.30 · 波形 0.70 · トーン 0.35 | 2.00 → 4.00 s |
| `demo_orilla.ogg` | `orilla` | 速さ 0.35 · 深さ 0.55 · ミックス 0.50 · スムージング 0.50 · ローパスゲート 0.80 · 感度 0.50 | 3.00 → 3.80 s |
| `demo_baldosa.ogg` | `baldosa` | タイム 0.55 · ディケイ 0.70 · ミックス 0.45 · モジュレーション 0.50 · トーン 0.40 · サンプリング周波数 0.30 | 2.60 → 3.40 s |
| `demo_eco_casero.ogg` | `eco_casero` | タイム 0.75 · フィードバック 0.55 · ミックス 0.45 · 汚れ 0.80 · モジュレーション 0.30 · トーン 0.30 | — |
| `demo_relevo.ogg` | `relevo` | タイム 0.60 · チューニング 0.50 · ミックス 0.60 · ビブラート 0.35 · トーン 0.60 · レベル 0.70 | 1.00 → 1.10 s, 4.00 → 4.10 s |
| `demo_frenada.ogg` | `frenada` | タイム 0.50 · フィードバック 0.50 · ミックス 0.45 · ブレーキ時間 0.50 · 始動時間 0.40 · ワウとフラッター 0.40 | 2.50 → 3.50 s |
| `demo_resbalon.ogg` | `resbalon` | 速さ 0.58 · フィードバック 0.70 · ミックス 0.55 · 長さ 0.70 · トーン 0.40 · タイム 0.20 | 4.00 → 7.00 s |
| `demo_tartamudeo.ogg` | `tartamudeo` | スレッショルド 0.30 · 長さ 0.45 · ミックス 0.50 · リピート回数 0.60 | — |
| `demo_dos_ecos.ogg` | `dos_ecos` | タイム 0.85 · フィードバック 0.60 · ミックス 0.50 · 比率 0.90 · バランス 0.50 · 拡散 0.70 | 4.00 → 6.00 s |
| `demo_viento.ogg` | `viento` | 速さ 0.50 · レゾナンス 0.60 · ミックス 0.50 · 感度 0.70 · 周波数 0.50 · レベル 0.40 | 2.50 → 3.50 s |
| `demo_compas.ogg` | `compas` | タイム 0.60 · フィードバック 0.45 · ミックス 0.45 · subdivisión 0.10 · segunda toma 1.00 · トーン 0.70 | 0.50 → 0.55 s, 1.00 → 1.05 s |
| `demo_espiral.ogg` | `espiral` | 音程 0.92 · 第2声部 0.08 · ミックス 0.55 · タイム 0.40 · フィードバック 0.70 · ディケイ 0.60 | 3.00 → 4.50 s |
| `demo_swell_ritmico.ogg` | `swell_ritmico` | 立ち上がり 0.40 · 波形 0.20 · ミックス 0.50 · ディケイ 0.70 · ドリフト 0.40 · 感度 0.50 | 0.00 → 0.05 s, 0.22 → 0.27 s |
| `demo_semilla.ogg` | `semilla` | ディケイ 0.80 · ダンピング 0.35 · ミックス 0.50 · semilla 0.60 · densidad 0.80 · モジュレーション 0.45 | 4.00 → 6.50 s |
| `demo_arpegio.ogg` | `arpegio` | 速さ 0.45 · notas 1.00 · ミックス 0.50 · モード 0.00 · エコー 0.40 · ディケイ 0.60 | 3.00 → 5.00 s |
| `demo_cadena_eco_y_muelle.ogg` | Eco y muelle: `delay` → `spring` | pot0 0.55 · pot1 0.40 · pot2 0.35 · pot3 0.60 · pot4 0.40 · pot5 0.00 | — |
| `demo_cadena_flor_al_reves.ogg` | Flor al revés: `reverse` → `bloom` | pot0 0.60 · pot1 0.40 · pot2 0.50 · pot3 0.80 · pot4 0.55 · pot5 0.40 | — |
| `demo_cadena_organo_infinito.ogg` | Órgano infinito: `octava` → `infinite` | pot0 0.60 · pot1 0.40 · pot2 0.00 · pot3 0.10 · pot4 0.50 · pot5 0.00 | — |
| `demo_cadena_shimmer_con_vibrato.ogg` | Shimmer con vibrato: `vibrato` → `shimmer` | pot0 0.30 · pot1 0.40 · pot2 0.00 · pot3 0.75 · pot4 0.55 · pot5 0.60 | — |
| `demo_cadena_cuerdas_en_ola.ogg` | Cuerdas en ola: `tremolo` → `ensemble` | pot0 0.15 · pot1 0.70 · pot2 0.00 · pot3 0.80 · pot4 0.50 · pot5 0.70 | — |
| `demo_cadena_fuzz_en_la_nube.ogg` | Fuzz en la nube: `saturacion` → `cloud` | pot0 0.60 · pot1 0.00 · pot2 0.00 · pot3 0.70 · pot4 0.50 · pot5 0.60 | — |

Ogg Vorbis、48,828 Hz（ADR 0005、スペイン語）。レンダリングは 24 ビットでビット精度です。ノブとプログラムは `docs/programas.ja.md` にあります。
