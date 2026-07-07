# python unzip_with_dialog_2.py
# ==========================================================
# ファイル名: unzip_with_dialog.py
# ZIP一括解凍ツール（フォルダ選択ダイアログ版）
# ----------------------------------------------------------
# ■ 作成日: 2025年10月22日
# ■ 更新日: 2026年03月30日
#
# ■ 概要
#   フォルダ以下を再帰的に走査し、ZIPファイルを処理します。
#   - 同名フォルダが既に存在する → 解凍済みとみなしZIPを削除
#   - 同名フォルダが存在しない   → 解凍してからZIPを削除
#   2回目以降も安全に実行できます。
#
# ■ 使い方
#   1. スクリプトを実行するとフォルダ選択ダイアログが開く
#   2. 対象フォルダを選択すると自動的に処理開始
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
    root.withdraw()
    return filedialog.askdirectory(title="ZIPファイルのあるフォルダを選択してください")


def process_zips(target_dir):
    """
    指定フォルダ以下を再帰的に走査してZIPを処理する。

    処理ルール:
        - 同名フォルダあり → 解凍済みとみなしZIPだけ削除
        - 同名フォルダなし → 解凍してからZIPを削除
    """
    if not target_dir:
        messagebox.showwarning("警告", "フォルダが選択されていません。")
        return

    # 再帰的にZIPを収集
    zip_files = []
    for dirpath, _dirnames, filenames in os.walk(target_dir):
        for filename in filenames:
            if filename.lower().endswith(".zip"):
                zip_files.append(os.path.join(dirpath, filename))

    if not zip_files:
        messagebox.showinfo("情報", "ZIPファイルが見つかりませんでした。")
        return

    extracted_count = 0
    skipped_count = 0
    deleted_count = 0
    errors = []

    for zip_path in zip_files:
        parent_dir = os.path.dirname(zip_path)
        folder_name = os.path.splitext(os.path.basename(zip_path))[0]
        extract_path = os.path.join(parent_dir, folder_name)

        try:
            if os.path.isdir(extract_path):
                # 同名フォルダあり → 解凍済みとみなしてスキップ
                print(f"Skip (already exists): {zip_path}")
                skipped_count += 1
            else:
                # 同名フォルダなし → 解凍する
                os.makedirs(extract_path, exist_ok=True)
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(extract_path)
                print(f"Extracted: {zip_path} → {extract_path}")
                extracted_count += 1

            # どちらの場合もZIPを削除
            os.remove(zip_path)
            print(f"Deleted:   {zip_path}")
            deleted_count += 1

        except Exception as e:
            errors.append(f"{zip_path}: {e}")
            print(f"ERROR: {zip_path}: {e}")

    # 完了メッセージ
    msg_lines = [
        f"処理完了: {len(zip_files)} 個のZIPを処理しました。",
        f"  ・新規解凍: {extracted_count} 個",
        f"  ・解凍済みスキップ: {skipped_count} 個",
        f"  ・ZIP削除: {deleted_count} 個",
    ]
    if errors:
        msg_lines.append(f"\n⚠ エラー ({len(errors)} 件):")
        msg_lines.extend(errors)
        messagebox.showwarning("完了（エラーあり）", "\n".join(msg_lines))
    else:
        messagebox.showinfo("完了", "\n".join(msg_lines))


if __name__ == "__main__":
    folder = select_directory()
    process_zips(folder)