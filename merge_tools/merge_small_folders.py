# python -m merge_tools.merge_small_folders.py
# 指定フォルダ内で、ファイル数がN個以下のフォルダを検出し、確認後にまとめてコピー・元を削除する

import sys
from pathlib import Path
from datetime import datetime
import shutil
import tkinter as tk
from tkinter import messagebox, simpledialog

sys.path.append(str(Path(__file__).resolve().parent.parent))
from common.common import select_directory

# 設定
root_dir_str = select_directory(title="探索する親フォルダを選択してください")
if not root_dir_str:
    print("[警告]", "フォルダが選択されていません。")
    sys.exit()
ROOT_DIR = Path(root_dir_str)

root = tk.Tk()
root.withdraw()
N = simpledialog.askinteger(
    "ファイル数の上限",
    "フォルダ内が何個以下のファイルを対象にしますか？",
    initialvalue=10,
    minvalue=0,
)
if N is None:
    print("[警告]", "ファイル数の上限が入力されていません。")
    sys.exit()

print(f"ROOT_DIR: {ROOT_DIR}")

targets = []
for folder in ROOT_DIR.iterdir():
    if not folder.is_dir():
        continue

    files = [p for p in folder.iterdir() if p.is_file()]

    if len(files) <= N:
        print(f"({len(files)} files): {folder.name} ")
        targets.append(folder)

if targets:
    folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_DIR = ROOT_DIR / folder_name

    if messagebox.askyesno("確認", f"{len(targets)} 個のフォルダをまとめますか？\n\n保存先: {OUTPUT_DIR}"):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        for folder in targets:
            files = [p for p in folder.iterdir() if p.is_file()]
            for file in files:
                dest = OUTPUT_DIR / f"{folder.name}_{file.name}"

                # 同名ファイルがある場合は連番を付ける
                counter = 1
                while dest.exists():
                    dest = OUTPUT_DIR / f"{folder.name}_{file.stem}_{counter}{file.suffix}"
                    counter += 1

                shutil.copy2(str(file), str(dest))
                print(f"  {file} -> {dest}")
                file.unlink()

            try:
                folder.rmdir()
                print(f"  削除: {folder}")
            except OSError:
                print(f"  削除スキップ（中身が残っている）: {folder}")
    else:
        print("キャンセルしました。")
