# python -m merge_tools.check_small_folders
# 指定フォルダ内で、ファイル数がN個以下のフォルダを一覧表示する（確認専用・操作なし）

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from common.common import select_directory

# 設定
ROOT_DIR = Path(select_directory(title="探索する親フォルダを選択してください"))
N = 10  # ファイル数の上限

print(f"ROOT_DIR: {ROOT_DIR}")

for folder in ROOT_DIR.iterdir():
    if not folder.is_dir():
        continue

    files = [p for p in folder.iterdir() if p.is_file()]

    if len(files) <= N:
        print(f"({len(files)} files): {folder.name} ")
