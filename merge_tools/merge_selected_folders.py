# python -m merge_tools.merge_selected_folders.py
# 手動で選んだ複数フォルダを、確認後にまとめてコピー・元を削除する

import sys
from pathlib import Path
from datetime import datetime
import shutil
import tkinter as tk
from tkinter import messagebox

sys.path.append(str(Path(__file__).resolve().parent.parent))
from common.common import select_directory


def get_folder_paths():
    """複数フォルダのパスを貼り付けるウィンドウを表示し、パスのリストを返す"""
    root = tk.Tk()
    root.title("merge_selected_folders.py - フォルダパス貼り付け")
    root.geometry("600x600")

    label = tk.Label(
        root,
        text=(
            "merge_selected_folders.py\n"
            "エクスプローラーで複数フォルダを選択 → 右クリック →「パスのコピー」\n"
            "した内容を下の欄に貼り付けてください（1行1パス）。\n"
            "「実行」を押すと、各フォルダの中身が「フォルダ名_ファイル名」に\n"
            "リネームされ、1つのフォルダにまとめられます。"
        ),
        justify="left",
        anchor="w",
    )
    label.pack(fill="x", padx=10, pady=10)

    text = tk.Text(root, wrap="none")
    text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    result = {"paths": []}

    def on_submit():
        content = text.get("1.0", "end")
        paths = []
        for line in content.splitlines():
            line = line.strip().strip('"')
            if line:
                paths.append(line)
        result["paths"] = paths
        root.destroy()

    button = tk.Button(root, text="実行", command=on_submit)
    button.pack(pady=(0, 10))

    root.mainloop()
    return result["paths"]


def main():
    raw_paths = get_folder_paths()

    folders = []
    for raw_path in raw_paths:
        p = Path(raw_path)
        if p.is_dir():
            folders.append(p)
        else:
            print(f"スキップ（フォルダではない）: {raw_path}")

    if not folders:
        messagebox.showwarning("警告", "有効なフォルダが指定されていません。")
        return

    output_parent_str = select_directory(title="まとめ先の親フォルダを選択してください")
    if not output_parent_str:
        messagebox.showwarning("警告", "まとめ先フォルダが選択されていません。")
        return

    output_parent = Path(output_parent_str)
    folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = output_parent / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"対象フォルダ数: {len(folders)}")
    print(f"OUTPUT_DIR: {output_dir}")

    for folder in folders:
        files = [p for p in folder.iterdir() if p.is_file()]
        print(f"{folder.name} ({len(files)} files)")
        for file in files:
            dest = output_dir / f"{folder.name}_{file.name}"

            # 同名ファイルがある場合は連番を付ける
            counter = 1
            while dest.exists():
                dest = output_dir / f"{folder.name}_{file.stem}_{counter}{file.suffix}"
                counter += 1

            shutil.copy2(str(file), str(dest))
            print(f"  {file} -> {dest}")
            file.unlink()

        try:
            folder.rmdir()
            print(f"  削除: {folder}")
        except OSError:
            print(f"  削除スキップ（中身が残っている）: {folder}")

    messagebox.showinfo("完了", f"{len(folders)} 個のフォルダをまとめました。\n{output_dir}")


if __name__ == "__main__":
    main()
