import tkinter as tk
from tkinter import filedialog


def select_directory(title="フォルダを選択してください"):
    """フォルダ選択ダイアログを開いてパスを返す"""
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title=title)
