# QR Generator

URLやテキストからQRコードを生成するGUIツールです。

## 機能

- URL・テキストからQRコードをリアルタイム生成
- 前景色・背景色をカラーピッカーまたはHEXコードで設定
- サイズ選択：S（256px）/ M（512px）/ L（1024px）
- 余白設定：1 / 2 / 4マス
- PNG・JPEG形式で保存
- 保存先：ダウンロードフォルダに自動保存
- 同名ファイルの上書き確認ダイアログあり
- Windows・macOS 対応

## 必要な環境

- Python 3.10 以上

## インストール

```bash
pip install qrcode[pil] pillow customtkinter tkcolorpicker
```

## 使い方

```bash
python qr_generator.py
```

1. URL またはテキストを入力欄に入力
2. 「生成」ボタンを押すか Enter キーで QRコードを生成
3. 色・サイズ・余白・保存形式を必要に応じて設定
4. 「ダウンロードフォルダに保存」ボタンで保存

## サイズの目安

| サイズ | 解像度 | 用途 |
|--------|--------|------|
| S | 256px | 名刺・SNS |
| M | 512px | チラシ・Web |
| L | 1024px | ポスター・印刷 |
