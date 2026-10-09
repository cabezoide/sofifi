<!-- i18n: fuente=BOM.md sha=bfc6e2d73f57 estado=al_dia -->
# BOM · SOFIFI のハードウェア

ペダルの購入リストです。リンクは **2026 年 10 月 7 日** に確認しました。[V] = ページが表示され、商品が販売中。[?] = ページを表示できなかった。価格はその日のもので、送料を含みません。価格は変わります。

## 今すぐ必要なもの（フェーズ 08 まで）

| # | 品目 | 用途 | 概算価格 | 購入先 |
|---|---|---|---|---|
| 1 | **Sipeed Tang Primer 25K Dock Kit**（FPGA GW5A-LV25 + USB-C デバッガー、3 つの PMOD、40 ピンコネクター付きの Dock） | DSP コアを実行する FPGA。Dock のデバッガーが FPGA に書き込み、UART も兼ねます。別のデバッガーは不要です。 | 29 USD | [V] [SpotPear（Sipeed の販売代理店）](https://spotpear.com/shop/Sipeed-FPGA-Tang-Primer-25K-Dock-Gowin-PMOD-SDRAM-GW5A-LV25MG121-RISCV-Retro-Game-Open-Source-linux/Tang-Primer-25K-Dock-Kit.html) · [?] [AliExpress の Sipeed 公式ストア](https://www.aliexpress.us/item/3256806038278266.html) |
| 2 | **Sipeed PMOD TF-CARD**（microSD リーダー） | microSD を SPI モードで読みます（フェーズ 08）。Dock の J6 コネクターに挿します。テスト用トップは 2 つのリビジョンの両方を認識します。 | — | 確認済みのリンクなし。公式資料：[V] [Sipeed wiki](https://wiki.sipeed.com/hardware/en/tang/tang-PMOD/FPGA_PMOD.html)。Sipeed の PMOD キット：[?] [AliExpress](https://www.aliexpress.us/item/1005006265716790.html)。「Sipeed Tang PMOD TF-CARD」で検索してください。 |
| 3 | **64 GB の microSD**（例：Samsung EVO Select） | プログラムのバンクを保存します。バンクは最大で約 14 MB（1,024 プログラム）を使います。SDHC か SDXC でなければなりません：バージョン 1 のカードは動作しません。 | 15 USD | [V] [Samsung](https://www.samsung.com/us/computing/memory-storage/memory-cards/evo-select-adapter-microsdxc-64gb-mb-me64ka-am/)（10 月 7 日に品切れ）。代替品：SanDisk Ultra 64 GB。 |
| 4 | **データ通信対応の USB-A to USB-C ケーブル** | Dock を PC に接続します。 | 5 USD | [V] [Adafruit #4474](https://www.adafruit.com/product/4474) |

## フェーズ 09 から 11 で足りないもの

| # | 品目 | 用途 | フェーズ | 概算価格 | 購入先 |
|---|---|---|---|---|---|
| 5 | **Digilent Pmod I2S2**（ADC CS5343 + DAC CS4344） | 24 bit ステレオのオーディオ入出力。推奨のコーデックです。 | 11 | 30 USD | [V] [DigiKey 410-379](https://www.digikey.com/en/products/detail/digilent-inc/410-379/9445907) · [?] [Digilent](https://digilent.com/shop/pmod-i2s2-stereo-audio-input-and-output) |
| 6a | **PCM1808** ADC モジュール（I2S） | Pmod I2S2 の代替：オーディオ入力。 | 11 | 13 USD | [V] [Newegg](https://www.newegg.com/p/2TP-005G-00609)（第三者の出品：最も信頼性の低いリンク） |
| 6b | **Adafruit PCM5102** I2S DAC | Pmod I2S2 の代替：オーディオ出力。 | 11 | 5 USD | [V] [Adafruit #6250](https://www.adafruit.com/product/6250) |
| 7 | **Microchip MCP3208-CI/P**（12 bit・8 チャンネルの SPI ADC） | 6 個のポテンショメーターを読み取ります。 | 09 | 3 USD | [V] [DigiKey](https://www.digikey.com/en/products/detail/microchip-technology/MCP3208-CI-P/305928) |
| 8 | **B10K リニアポテンショメーター** ×6 | ペダルのノブ。 | 09 | 1 個 0.39 USD | [V] [Tayda A-5523](https://www.taydaelectronics.com/tayda-b10k-ohm-linear-taper-potentiometer-round-shaft-pc-mount.html) |
| 9 | **SPST モーメンタリー・ソフトタッチのフットスイッチ** ×2 | Bypass と freeze。それまでは Dock のボタンを使えます。 | 09 | 1 個 3 USD | [V] [Tayda](https://www.taydaelectronics.com/spst-momentary-soft-touch-push-button-stomp-foots-pedal-switch-on-off.html) |
| 10 | **128×64 の SSD1306 OLED** | プリセットと各ノブの機能を 4 言語で表示します。 | 10 | 20 USD | [V] [Adafruit #938](https://www.adafruit.com/product/938)（10 月 7 日に品切れ） |
| 11 | **入力バッファー**（JFET またはオペアンプ） | ギター（高インピーダンス）を ADC の入力に合わせます。バッファー付きのペダルならどれでも使えます。 | 11 | 0.50 USD（PCB のみ） | [V] [PedalPCB Simple JFET Buffer](https://www.pedalpcb.com/product/jfetbuffer/) · [?] [PedalPCB MicroBuffer](https://www.pedalpcb.com/product/pcb678/) |

## 将来必要なもの

| # | 品目 | 用途 | 概算価格 | 購入先 |
|---|---|---|---|---|
| 12 | Tang Primer 25K 用 **Sipeed SDRAM モジュール**（40 ピン） | 外部メモリー：長いルーパーと数秒のグラニュラー（フェーズ 12 以降）。 | 10 USD | [V] [SpotPear「Only-SDRAM」](https://spotpear.com/shop/Sipeed-FPGA-Tang-Primer-25K-Dock-Gowin-PMOD-SDRAM-GW5A-LV25MG121-RISCV-Retro-Game-Open-Source-linux/Only-SDRAM.html)（ページに容量の記載なし。Sipeed wiki では 32 MB [?]） |

## 概算の合計

- フェーズ 08 まで：**約 50 USD**（ボード、microSD、ケーブル。PMOD リーダーの価格は未確認）。
- Pmod I2S2 を使った完成ペダル：**約 125 USD**。これにケース、ジャック、電源が加わります。これらはまだリストにありません（PCB と一緒に計画します）。

フェーズ 12 以降の基板（PCB、ケース、ジャック、電源）はこのリストにありません。アナログフロントエンドと一緒に設計します。
