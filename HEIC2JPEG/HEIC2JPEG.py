import tkinter as tk
from tkinter import filedialog
from pathlib import Path

from PIL import Image
from pillow_heif import register_heif_opener

# pillow-heif を PIL に登録することで、PIL が HEIC を読めるようになる
register_heif_opener()

# JPEG の保存品質（1〜95）。数字が大きいほど高画質・大容量
JPEG_QUALITY = 92


def select_folder():
    """GUIのフォルダ選択ダイアログを開き、選択したパスを返す"""

    root = tk.Tk()
    root.withdraw()  # tkinter のメインウィンドウは不要なので非表示にする
    folder = filedialog.askdirectory(title="HEICフォルダを選択")
    return folder


def convert_folder(folder_path):
    """指定フォルダ内の HEIC ファイルをまとめて JPEG に変換する"""

    input_dir = Path(folder_path)

    # 変換後の JPEG を格納するサブフォルダ。exist_ok=True で既存でもエラーにしない
    output_dir = input_dir / "jpeg_output"
    output_dir.mkdir(exist_ok=True)

    # glob で .heic を列挙。大文字小文字を両方拾うため suffix.lower() で統一
    files = list({f for f in input_dir.glob("*") if f.suffix.lower() == ".heic"})

    if not files:
        print("HEICファイルが見つかりません")
        return

    for file in files:

        # 出力ファイル名を決定。同名ファイルがあれば _2, _3 と連番を付けて上書きを防ぐ
        output_file = _unique_path(output_dir / (file.stem + ".jpg"))

        try:
            with Image.open(file) as img:

                # HEIC は RGBA や P モードのことがある。JPEG は RGB のみ対応のため変換
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # optimize=True でハフマンテーブルを最適化し、少しファイルサイズを削減
                img.save(
                    output_file,
                    "JPEG",
                    quality=JPEG_QUALITY,
                    optimize=True
                )

            print(f"OK : {file.name}")

        except Exception as e:
            print(f"NG : {file.name}  {e}")

    print("\n変換完了")


def _unique_path(path: Path) -> Path:
    """同名ファイルが存在する場合、stem_2.jpg のように連番を付けて返す"""

    if not path.exists():
        return path

    counter = 2
    while True:
        candidate = path.with_stem(f"{path.stem}_{counter}")
        if not candidate.exists():
            return candidate
        counter += 1


def main():

    folder = select_folder()

    if not folder:
        print("フォルダが選択されませんでした")
        return

    convert_folder(folder)


if __name__ == "__main__":
    main()
