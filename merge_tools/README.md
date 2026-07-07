# merge_tools

フォルダの中身をファイル数基準でまとめるスクリプト群。共通処理は `../common/common.py` を参照。

- `check_small_folders.py` — ファイル数がN個以下のフォルダを一覧表示するだけ（確認専用・操作なし）
- `merge_small_folders.py` — 上記の対象フォルダを検出し、確認後にまとめてコピー・元を削除する
- `merge_selected_folders.py` — 手動で選んだ複数フォルダを、確認後にまとめてコピー・元を削除する
