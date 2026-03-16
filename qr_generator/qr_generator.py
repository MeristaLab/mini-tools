# ============================================================
#  qr_generator.py  —  QRコード生成ツール
#  使い方：python qr_generator.py
#
#  必要なライブラリのインストール：
#    pip install qrcode[pil] pillow customtkinter tkcolorpicker
#
#  動作確認環境：
#    Python 3.10 以上 / Windows・macOS 対応
# ============================================================

import os
import re
import sys
import subprocess

import customtkinter as ctk          # モダンなデザインの tkinter ラッパー
from tkcolorpicker import askcolor   # カラーピッカーダイアログ
from PIL import Image                # 画像処理（リサイズ・変換）
import qrcode                        # QRコード生成

# ============================================================
#  OS判定
#  sys.platform で実行環境を判定し、サウンド処理などを分岐させる
# ============================================================

IS_WINDOWS = sys.platform == "win32"
IS_MAC     = sys.platform == "darwin"

# ============================================================
#  設定：ここを変えると初期値が変わります
# ============================================================

DEFAULT_TEXT       = "https://example.com"  # 起動時に入力欄に表示されるテキスト
DEFAULT_FG_COLOR   = "#000000"              # 前景色（QRコードの色）
DEFAULT_BG_COLOR   = "#ffffff"              # 背景色
DEFAULT_SIZE_LABEL = "M"                   # 起動時のサイズ（"S" / "M" / "L"）
DEFAULT_BORDER     = 2                     # 余白のマス数（1 / 2 / 4）
DEFAULT_FORMAT     = "PNG"                 # 保存形式（"PNG" / "JPEG"）

# サイズ定義：ラベル → (ピクセル数, 説明)
# dict でまとめることで、ループで UI を自動生成できる
SIZE_OPTIONS = {
    "S": (256,  "名刺・SNS"),
    "M": (512,  "チラシ・Web"),
    "L": (1024, "ポスター・印刷"),
}

# 余白定義：マス数 → 説明
# QRコードの規格では最低4マスの余白が推奨されている
BORDER_OPTIONS = {
    1: "最小（Web・デジタル向け）",
    2: "推奨（SNS・チラシ向け）",
    4: "規格準拠（印刷・公式向け）",
}

# ============================================================
#  テーマ設定
#  ctk の見た目をダークモードに設定。起動前に呼ぶ必要がある
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


# ============================================================
#  サウンド・通知ユーティリティ
# ============================================================

def play_alert_sound():
    """上書き確認ダイアログを開く時に鳴らすシステム警告音"""
    try:
        if IS_WINDOWS:
            import winsound
            # MB_ICONEXCLAMATION は「!」アイコンの警告音
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        elif IS_MAC:
            # afplay は macOS 標準のコマンドライン音声再生ツール
            subprocess.Popen(["afplay", "/System/Library/Sounds/Funk.aiff"])
    except Exception:
        pass  # 音が鳴らなくてもアプリは続行する


def play_save_sound():
    """保存完了時に鳴らすシステム音"""
    try:
        if IS_WINDOWS:
            import winsound
            winsound.MessageBeep(winsound.MB_OK)
        elif IS_MAC:
            subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"])
    except Exception:
        pass


# ============================================================
#  カラースウォッチボタン
#  ctk.CTkButton を継承し、クリックでカラーピッカーを開く独自ボタン
# ============================================================

class ColorSwatch(ctk.CTkButton):
    """クリックするとカラーピッカーを開くボタン"""
    def __init__(self, master, color, on_change, **kwargs):
        super().__init__(
            master,
            text="",           # 文字なし（色だけ表示）
            width=32,
            height=32,
            corner_radius=6,
            fg_color=color,    # ボタン自体の背景色を選択中の色にする
            hover_color=color,
            border_width=1,
            border_color="#555555",
            command=self._open_picker,
            **kwargs,
        )
        self._color = color
        self._on_change = on_change  # 色が変わった時に呼ばれるコールバック関数

    def _open_picker(self):
        """カラーピッカーを開き、選択された色を反映する"""
        result = askcolor(color=self._color, title="色を選択")
        # result は ((R, G, B), "#rrggbb") のタプル。キャンセル時は (None, None)
        if result and result[1]:
            self.set_color(result[1])
            self._on_change(result[1])  # 親ウィジェットに変更を通知

    def set_color(self, color):
        """ボタンの表示色を更新する"""
        self._color = color
        self.configure(fg_color=color, hover_color=color)


# ============================================================
#  メインアプリ
#  ctk.CTk（メインウィンドウ）を継承してアプリ全体を管理する
# ============================================================

class QRGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QR Generator")
        self.resizable(False, False)  # ウィンドウサイズ変更を禁止

        # 内部状態：色と生成済み画像を保持する
        self.fg_color = DEFAULT_FG_COLOR
        self.bg_color = DEFAULT_BG_COLOR
        self.qr_image = None  # 保存用 PIL Image（未生成時は None）

        self._build_ui()
        self._generate()  # 起動時に1回生成してプレビューを表示

    # ----------------------------------------------------------
    #  UI構築
    #  各セクションをフレームで分けて grid レイアウトで配置する
    # ----------------------------------------------------------
    def _build_ui(self):
        # column 0 を可変幅にすることで横幅いっぱいに広げる
        self.grid_columnconfigure(0, weight=1)
        pad = {"padx": 16, "pady": 6}

        # ── ① URL入力 ─────────────────────────────────────
        frame_url = ctk.CTkFrame(self)
        frame_url.grid(row=0, column=0, sticky="ew", **pad)
        frame_url.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_url, text="URL / テキスト",
                     font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 4))

        self.text_var = ctk.StringVar(value=DEFAULT_TEXT)
        entry = ctk.CTkEntry(frame_url, textvariable=self.text_var,
                             width=380, height=34, font=ctk.CTkFont(size=12))
        entry.grid(row=1, column=0, padx=(12, 6), pady=(0, 10), sticky="ew")
        # Enter キーでも生成できるようにイベントをバインド
        entry.bind("<Return>", lambda e: self._generate())

        ctk.CTkButton(frame_url, text="生成", width=72, height=34,
                      command=self._generate).grid(
            row=1, column=1, padx=(0, 12), pady=(0, 10))

        # ── ② 色設定 ──────────────────────────────────────
        frame_color = ctk.CTkFrame(self)
        frame_color.grid(row=1, column=0, sticky="ew", **pad)

        ctk.CTkLabel(frame_color, text="色  —  即時反映",
                     font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 6))

        # fg_color="transparent" でフレームの背景を透明にし、親と馴染ませる
        color_inner = ctk.CTkFrame(frame_color, fg_color="transparent")
        color_inner.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

        # 前景色（スウォッチ + HEXテキスト入力）
        ctk.CTkLabel(color_inner, text="前景色").grid(row=0, column=0, padx=(0, 6))
        self.fg_swatch = ColorSwatch(color_inner, self.fg_color, self._on_fg_change)
        self.fg_swatch.grid(row=0, column=1, padx=(0, 4))
        self.fg_hex_var = ctk.StringVar(value=self.fg_color)
        fg_entry = ctk.CTkEntry(color_inner, textvariable=self.fg_hex_var,
                                width=80, height=32)
        fg_entry.grid(row=0, column=2, padx=(0, 24))
        fg_entry.bind("<Return>",   lambda e: self._apply_hex("fg"))
        fg_entry.bind("<FocusOut>", lambda e: self._apply_hex("fg"))  # フォーカスが外れた時も反映

        # 背景色
        ctk.CTkLabel(color_inner, text="背景色").grid(row=0, column=3, padx=(0, 6))
        self.bg_swatch = ColorSwatch(color_inner, self.bg_color, self._on_bg_change)
        self.bg_swatch.grid(row=0, column=4, padx=(0, 4))
        self.bg_hex_var = ctk.StringVar(value=self.bg_color)
        bg_entry = ctk.CTkEntry(color_inner, textvariable=self.bg_hex_var,
                                width=80, height=32)
        bg_entry.grid(row=0, column=5)
        bg_entry.bind("<Return>",   lambda e: self._apply_hex("bg"))
        bg_entry.bind("<FocusOut>", lambda e: self._apply_hex("bg"))

        # ── ③ サイズ（左）＋ 余白（右）横並び ────────────
        frame_bottom = ctk.CTkFrame(self)
        frame_bottom.grid(row=2, column=0, sticky="ew", **pad)
        frame_bottom.grid_columnconfigure(0, weight=1)
        frame_bottom.grid_columnconfigure(2, weight=1)

        # 左：サイズ（ラジオボタンを dict からループ生成）
        frame_size = ctk.CTkFrame(frame_bottom, fg_color="transparent")
        frame_size.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=(10, 4))

        ctk.CTkLabel(frame_size, text="サイズ",
                     font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 4))

        self.size_var = ctk.StringVar(value=DEFAULT_SIZE_LABEL)
        for i, (label, (px, desc)) in enumerate(SIZE_OPTIONS.items()):
            ctk.CTkRadioButton(
                frame_size,
                text=f"{label}  {desc}（{px}px）",
                variable=self.size_var,   # 同じ変数を共有することでグループ化
                value=label,
                command=self._generate,   # 選択変更時に即再生成
            ).grid(row=i + 1, column=0, sticky="w", pady=2)

        # 区切り線（幅1pxのフレームで代用）
        ctk.CTkFrame(frame_bottom, width=1, fg_color="#444444").grid(
            row=0, column=1, sticky="ns", pady=10)

        # 右：余白
        frame_border = ctk.CTkFrame(frame_bottom, fg_color="transparent")
        frame_border.grid(row=0, column=2, sticky="nsew", padx=(12, 12), pady=(10, 4))

        ctk.CTkLabel(frame_border, text="余白",
                     font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 4))

        self.border_var = ctk.IntVar(value=DEFAULT_BORDER)
        for i, (masu, desc) in enumerate(BORDER_OPTIONS.items()):
            ctk.CTkRadioButton(
                frame_border,
                text=f"{masu}マス  {desc}",
                variable=self.border_var,
                value=masu,
                command=self._generate,
            ).grid(row=i + 1, column=0, sticky="w", pady=2)

        # ── ④ プレビュー ──────────────────────────────────
        frame_preview = ctk.CTkFrame(self)
        frame_preview.grid(row=3, column=0, sticky="ew", **pad)
        frame_preview.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_preview, text="プレビュー",
                     font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 6))

        # 画像を表示するラベル（image プロパティに CTkImage をセットする）
        self.preview_label = ctk.CTkLabel(frame_preview, text="")
        self.preview_label.grid(row=1, column=0, pady=4)

        # ステータステキスト（生成状態をユーザーに伝える）
        self.status_var = ctk.StringVar(value="生成中...")
        ctk.CTkLabel(frame_preview, textvariable=self.status_var,
                     text_color="gray", font=ctk.CTkFont(size=11)).grid(
            row=2, column=0, pady=(0, 10))

        # ── ⑤ 保存 ────────────────────────────────────────
        frame_save = ctk.CTkFrame(self)
        frame_save.grid(row=4, column=0, sticky="ew", **pad)
        frame_save.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_save, text="保存",
                     font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 6))

        fmt_row = ctk.CTkFrame(frame_save, fg_color="transparent")
        fmt_row.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 8))

        ctk.CTkLabel(fmt_row, text="保存形式").grid(row=0, column=0, padx=(0, 10))
        self.fmt_var = ctk.StringVar(value=DEFAULT_FORMAT)
        for i, fmt in enumerate(["PNG", "JPEG"]):
            ctk.CTkRadioButton(fmt_row, text=fmt,
                               variable=self.fmt_var, value=fmt).grid(
                row=0, column=i + 1, padx=10)

        ctk.CTkButton(frame_save, text="ダウンロードフォルダに保存",
                      height=36, command=self._save).grid(
            row=2, column=0, padx=12, pady=(0, 12), sticky="ew")

    # ----------------------------------------------------------
    #  QR生成
    #  qrcode ライブラリで QR を作り、PIL Image に変換してプレビューに表示
    # ----------------------------------------------------------
    def _generate(self):
        text = self.text_var.get().strip()
        if not text:
            self.status_var.set("テキストを入力してください")
            return

        px, _  = SIZE_OPTIONS[self.size_var.get()]
        border = self.border_var.get()

        # QRCode オブジェクト生成
        # version=None で内容に応じて自動選択、ERROR_CORRECT_H は最高レベルの誤り訂正
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=max(1, px // 25),  # 1マスのピクセル数（出力サイズから逆算）
            border=border,
        )
        qr.add_data(text)
        qr.make(fit=True)  # fit=True でデータに最適なバージョンに自動調整

        # PIL Image として取り出す。.convert("RGB") で確実に RGB にしておく
        self.qr_image = qr.make_image(
            fill_color=self.fg_color,
            back_color=self.bg_color,
        ).convert("RGB")

        # プレビューは 200px 固定にリサイズ（NEAREST はドットを滲ませない補間方式）
        preview = self.qr_image.resize((200, 200), Image.NEAREST)
        # CTkImage は light/dark 両テーマに対応した画像クラス
        self._tk_image = ctk.CTkImage(light_image=preview, dark_image=preview,
                                      size=(200, 200))
        self.preview_label.configure(image=self._tk_image)

        size_label = self.size_var.get()
        self.status_var.set(f"{size_label}（{px}px）/ 余白 {border}マス で生成しました")

    # ----------------------------------------------------------
    #  色変更ハンドラ
    #  ColorSwatch からコールバックで呼ばれ、内部状態を更新して再生成する
    # ----------------------------------------------------------
    def _on_fg_change(self, color):
        self.fg_color = color
        self.fg_hex_var.set(color)  # テキスト入力欄にも反映
        self._generate()

    def _on_bg_change(self, color):
        self.bg_color = color
        self.bg_hex_var.set(color)
        self._generate()

    def _apply_hex(self, which):
        """HEX テキスト入力から色を反映する。正規表現で形式チェックしてから適用"""
        val = (self.fg_hex_var if which == "fg" else self.bg_hex_var).get().strip()
        # #RRGGBB 形式かチェック（不正な値は無視）
        if re.fullmatch(r"#[0-9A-Fa-f]{6}", val):
            if which == "fg":
                self.fg_color = val
                self.fg_swatch.set_color(val)
                self._generate()
            else:
                self.bg_color = val
                self.bg_swatch.set_color(val)
                self._generate()

    # ----------------------------------------------------------
    #  保存（上書き確認 + 警告音 + トースト通知）
    # ----------------------------------------------------------
    def _save(self):
        if self.qr_image is None:
            return

        fmt = self.fmt_var.get()
        ext = "jpg" if fmt == "JPEG" else "png"

        # URL の特殊文字を _ に置換してファイル名に使う（最大20文字）
        slug = re.sub(r"[^\w]", "_", self.text_var.get().strip())[:20] or "qrcode"
        filename = f"qr_{slug}.{ext}"

        # os.path.expanduser("~") でホームディレクトリを取得し Downloads を繋げる
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(download_dir, exist_ok=True)
        save_path = os.path.join(download_dir, filename)

        # 同名ファイルがある場合は確認ダイアログを出す
        if os.path.exists(save_path):
            play_alert_sound()
            self._show_overwrite_dialog(save_path, filename, fmt)
        else:
            self._write_file(save_path, filename, fmt)

    def _show_overwrite_dialog(self, save_path, filename, fmt):
        """上書き確認ダイアログ（CTkToplevel でモーダルウィンドウを作る）"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("上書き確認")
        dialog.resizable(False, False)
        dialog.grab_set()  # このダイアログを閉じるまで親ウィンドウを操作不可にする

        ctk.CTkLabel(
            dialog,
            text=f"「{filename}」はすでに存在します。\n上書きしますか？",
            font=ctk.CTkFont(size=13),
            justify="center",
        ).pack(padx=24, pady=(20, 12))

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(padx=24, pady=(0, 16))

        # クロージャでダイアログの参照を保持しつつ処理を分岐
        def do_overwrite():
            dialog.destroy()
            self._write_file(save_path, filename, fmt)

        def do_cancel():
            dialog.destroy()
            self.status_var.set("保存をキャンセルしました")

        ctk.CTkButton(btn_row, text="上書き保存", width=120,
                      command=do_overwrite).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="キャンセル", width=120,
                      fg_color="transparent", border_width=1,
                      command=do_cancel).pack(side="left", padx=6)

    def _write_file(self, save_path, filename, fmt):
        """実際にファイルを書き出して保存完了ポップアップを表示"""
        # JPEG の場合のみ quality を指定（PNG には不要）
        save_kwargs = {"quality": 92} if fmt == "JPEG" else {}
        self.qr_image.save(save_path, fmt, **save_kwargs)
        self.status_var.set(f"保存しました → {save_path}")
        play_save_sound()
        self._show_save_dialog(filename, save_path)

    def _show_save_dialog(self, filename, save_path):
        """保存完了ポップアップ"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("保存完了")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f"保存しました",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(padx=24, pady=(20, 4))

        ctk.CTkLabel(
            dialog,
            text=save_path,
            font=ctk.CTkFont(size=11),
            text_color="gray",
        ).pack(padx=24, pady=(0, 16))

        ctk.CTkButton(dialog, text="OK", width=100,
                      command=dialog.destroy).pack(pady=(0, 16))


# ============================================================
#  起動
#  このファイルを直接実行した時だけアプリを起動する
#  （import された時には起動しない）
# ============================================================

if __name__ == "__main__":
    app = QRGeneratorApp()
    app.mainloop()
