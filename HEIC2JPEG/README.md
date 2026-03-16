# HEIC2JPEG

HEICファイルをまとめてJPEGに変換するGUIツールです。

## 機能

- フォルダ選択ダイアログでHEICファイルの入ったフォルダを指定
- フォルダ内のHEICファイルを一括でJPEGに変換
- 変換後のファイルは `jpeg_output/` サブフォルダに保存
- 同名ファイルが存在する場合は自動で連番を付けて保存（上書きなし）
- 保存品質：92（高画質）

## 必要な環境

- Python 3.10 以上

## インストール

```bash
pip install pillow pillow-heif
```

## 使い方

```bash
python HEIC2JPEG.py
```

1. 起動するとフォルダ選択ダイアログが開く
2. HEICファイルが入ったフォルダを選択
3. 同フォルダ内の `jpeg_output/` に変換済みJPEGが保存される

## 出力先

選択したフォルダの中に `jpeg_output/` フォルダが自動作成され、変換後のJPEGが保存されます。

```
選択したフォルダ/
├── photo1.heic
├── photo2.heic
└── jpeg_output/
    ├── photo1.jpg
    └── photo2.jpg
```
