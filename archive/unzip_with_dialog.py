# ==========================================================
# ファイル名: unzip_with_dialog.py
# ZIP一括解凍ツール（フォルダ選択ダイアログ版）
# ----------------------------------------------------------
# ■ 作成日: 2025年10月22日
#
# ■ 概要
#   実行時にフォルダ選択ダイアログを表示し、
#   選択されたフォルダ内のZIPファイルを一括解凍します。
#   手動操作・柔軟な利用に適したGUIタイプです。
#
# ■ 特徴
#   - UIダイアログでフォルダを指定可能
#   - 標準ライブラリ（tkinter）だけで動作
#   - 完了メッセージ付きで初心者にも扱いやすい
#
# ■ 使い方
#   1. スクリプトを実行するとフォルダ選択ダイアログが開く
#   2. 対象フォルダを選択すると自動的にZIPを解凍
#   3. 完了後、結果メッセージが表示される
# python -u "d:\EM,EI\unzip_with_dialog.py"
# ==========================================================


import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox

def select_directory():
    """フォルダ選択ダイアログを開いてパスを返す"""
    root = tk.Tk()
    root.withdraw()  # メインウィンドウ非表示
    folder = filedialog.askdirectory(title="ZIPファイルのあるフォルダを選択してください")
    return folder

def unzip_all_in_folder(target_dir):
    """指定フォルダ内のZIPファイルを一括解凍"""
    if not target_dir:
        messagebox.showwarning("警告", "フォルダが選択されていません。")
        return

    output_dir = target_dir
    os.makedirs(output_dir, exist_ok=True)

    zip_files = [f for f in os.listdir(target_dir) if f.lower().endswith(".zip")]

    if not zip_files:
        messagebox.showinfo("情報", "ZIPファイルが見つかりませんでした。")
        return

    for filename in zip_files:
        zip_path = os.path.join(target_dir, filename)
        folder_name = os.path.splitext(filename)[0]
        extract_path = os.path.join(output_dir, folder_name)
        os.makedirs(extract_path, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        print("Extracted:", filename, "→", extract_path)

    messagebox.showinfo("完了", f"{len(zip_files)} 個のZIPファイルを解凍しました。")

if __name__ == "__main__":
    folder = select_directory()
    unzip_all_in_folder(folder)
