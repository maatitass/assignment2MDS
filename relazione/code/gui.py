"""Simple Tkinter GUI for DCT image compression."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
from PIL import Image, ImageTk

from dct_utils import compress_image_array, load_bmp_grayscale


class CompressionApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Compressione DCT2")
        self.image_path: Path | None = None
        self.original_array: np.ndarray | None = None
        self.compressed_array: np.ndarray | None = None
        self.original_photo: ImageTk.PhotoImage | None = None
        self.compressed_photo: ImageTk.PhotoImage | None = None

        self.path_label = tk.Label(root, text="Nessuna immagine selezionata", anchor="w")
        self.path_label.grid(row=0, column=0, columnspan=4, sticky="ew", padx=10, pady=(10, 4))

        choose_button = tk.Button(root, text="Scegli BMP", command=self.choose_image)
        choose_button.grid(row=1, column=0, padx=10, pady=4, sticky="ew")

        tk.Label(root, text="F").grid(row=1, column=1, padx=(10, 4), sticky="e")
        self.block_entry = tk.Entry(root, width=8)
        self.block_entry.insert(0, "8")
        self.block_entry.grid(row=1, column=2, padx=4, pady=(4, 0))
        self.block_entry.bind("<KeyRelease>", lambda _event: self.update_parameter_help())
        self.f_hint_label = tk.Label(root, text="", anchor="w")
        self.f_hint_label.grid(row=2, column=2, sticky="w", padx=4, pady=(0, 4))

        tk.Label(root, text="d").grid(row=3, column=1, padx=(10, 4), sticky="e")
        self.cutoff_entry = tk.Entry(root, width=8)
        self.cutoff_entry.insert(0, "8")
        self.cutoff_entry.grid(row=3, column=2, padx=4, pady=(4, 0))
        self.cutoff_entry.bind("<KeyRelease>", lambda _event: self.update_parameter_help())
        self.d_hint_label = tk.Label(root, text="", anchor="w")
        self.d_hint_label.grid(row=4, column=2, sticky="w", padx=4, pady=(0, 4))

        compress_button = tk.Button(root, text="Comprimi", command=self.compress)
        compress_button.grid(row=1, column=3, rowspan=4, padx=10, pady=4, sticky="nsew")

        tk.Label(root, text="Originale").grid(row=5, column=0, columnspan=2, padx=10, pady=(10, 4))
        tk.Label(root, text="Compressa").grid(row=5, column=2, columnspan=2, padx=10, pady=(10, 4))

        self.original_canvas = tk.Canvas(root, width=420, height=420, bg="white", highlightthickness=1)
        self.original_canvas.grid(row=6, column=0, columnspan=2, padx=10, pady=4, sticky="nsew")
        self.original_canvas.bind("<Configure>", lambda _event: self.render_previews())

        self.compressed_canvas = tk.Canvas(root, width=420, height=420, bg="white", highlightthickness=1)
        self.compressed_canvas.grid(row=6, column=2, columnspan=2, padx=10, pady=4, sticky="nsew")
        self.compressed_canvas.bind("<Configure>", lambda _event: self.render_previews())

        self.status_label = tk.Label(root, text="", anchor="w")
        self.status_label.grid(row=7, column=0, columnspan=4, sticky="ew", padx=10, pady=10)

        for column in range(4):
            root.columnconfigure(column, weight=1)
        root.rowconfigure(6, weight=1)

        self.draw_placeholder(self.original_canvas, "Scegli una immagine BMP")
        self.draw_placeholder(self.compressed_canvas, "Premi Comprimi")
        self.update_parameter_help()

    def choose_image(self) -> None:
        initial_dir = Path(__file__).resolve().parent / "immagini"
        path = filedialog.askopenfilename(
            initialdir=initial_dir if initial_dir.exists() else Path.home(),
            title="Scegli una immagine BMP",
            filetypes=[("Immagini BMP", "*.bmp"), ("Tutti i file", "*.*")],
        )
        if path:
            try:
                self.image_path = Path(path)
                image, status = load_original_preview(self.image_path)
            except Exception as error:
                messagebox.showerror("Errore", str(error))
                return

            self.original_array = image
            self.compressed_array = None
            self.compressed_photo = None
            self.path_label.config(text=str(self.image_path))
            self.status_label.config(text=status)
            self.update_parameter_help()
            self.render_previews()

    def compress(self) -> None:
        if self.image_path is None:
            messagebox.showerror("Errore", "Scegli prima una immagine .bmp")
            return

        try:
            block_size = int(self.block_entry.get())
            cutoff = int(self.cutoff_entry.get())
            original, compressed, status = build_compression_preview(self.image_path, block_size, cutoff)
        except Exception as error:
            messagebox.showerror("Errore", str(error))
            return

        self.original_array = original
        self.compressed_array = compressed
        self.status_label.config(text=status)
        self.update_parameter_help()
        self.render_previews()

    def update_parameter_help(self) -> None:
        image_shape = self.original_array.shape if self.original_array is not None else None
        f_hint, d_hint = describe_parameter_hints(self.block_entry.get(), self.cutoff_entry.get(), image_shape)
        self.f_hint_label.config(text=f_hint)
        self.d_hint_label.config(text=d_hint)

    def render_previews(self) -> None:
        self.original_photo = self.draw_image(self.original_canvas, self.original_array, "Scegli una immagine BMP")
        self.compressed_photo = self.draw_image(self.compressed_canvas, self.compressed_array, "Premi Comprimi")

    def draw_image(
        self,
        canvas: tk.Canvas,
        image: np.ndarray | None,
        placeholder: str,
    ) -> ImageTk.PhotoImage | None:
        canvas.delete("all")
        if image is None:
            self.draw_placeholder(canvas, placeholder)
            return None

        canvas_width = max(canvas.winfo_width() - 12, 1)
        canvas_height = max(canvas.winfo_height() - 12, 1)
        photo = array_to_photo(image, canvas_width, canvas_height)
        canvas.create_image(canvas.winfo_width() // 2, canvas.winfo_height() // 2, image=photo, anchor="center")
        return photo

    def draw_placeholder(self, canvas: tk.Canvas, text: str) -> None:
        canvas.delete("all")
        width = max(canvas.winfo_width(), 420)
        height = max(canvas.winfo_height(), 420)
        canvas.create_text(width // 2, height // 2, text=text, fill="gray40")


def array_to_photo(image: np.ndarray, max_width: int = 420, max_height: int = 420) -> ImageTk.PhotoImage:
    pil_image = Image.fromarray(np.asarray(image, dtype=np.uint8))
    new_size = fit_preview_size(pil_image.size, (max_width, max_height))
    if new_size != pil_image.size:
        pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(pil_image)


def fit_preview_size(image_size: tuple[int, int], available_size: tuple[int, int]) -> tuple[int, int]:
    image_width, image_height = image_size
    available_width, available_height = available_size
    if image_width <= 0 or image_height <= 0 or available_width <= 0 or available_height <= 0:
        return (1, 1)

    scale = min(available_width / image_width, available_height / image_height)
    return (max(1, int(image_width * scale)), max(1, int(image_height * scale)))


def load_original_preview(path: str | Path) -> tuple[np.ndarray, str]:
    image = load_bmp_grayscale(path)
    height, width = image.shape
    status = f"Caricata {Path(path).name}: {width} x {height} pixel. Premi Comprimi per applicare la DCT2."
    return image, status


def build_compression_preview(
    path: str | Path,
    block_size: int,
    cutoff: int,
) -> tuple[np.ndarray, np.ndarray, str]:
    image = load_bmp_grayscale(path)
    cropped_original, compressed = compress_image_array(image, block_size, cutoff)
    status = (
        f"Dimensione originale: {image.shape[1]} x {image.shape[0]} pixel. "
        f"Dimensione usata: {cropped_original.shape[1]} x {cropped_original.shape[0]} pixel, "
        f"F={block_size}, d={cutoff}"
    )
    return image, compressed, status


def describe_parameter_hints(
    block_text: str,
    cutoff_text: str,
    image_shape: tuple[int, int] | None = None,
) -> tuple[str, str]:
    block_size = _parse_int(block_text)
    cutoff = _parse_int(cutoff_text)
    max_block = min(image_shape) if image_shape is not None else None

    if cutoff_text.strip() and (cutoff is None or cutoff < 0):
        f_hint = "d non valido"
    elif cutoff is not None and cutoff >= 0:
        min_block = (cutoff + 3) // 2
        f_hint = f"F min {min_block}"
        if max_block is not None:
            f_hint += f", max {max_block}"
            if min_block > max_block:
                f_hint += " (nessun valore valido)"
    elif max_block is not None:
        f_hint = f"F max {max_block}"
    else:
        f_hint = "F > 0"

    if block_text.strip() and (block_size is None or block_size <= 0):
        f_hint = "F > 0"
        d_hint = "Inserisci F"
    elif block_size is not None and block_size > 0:
        max_cutoff = 2 * block_size - 2
        d_hint = f"d da 0 a {max_cutoff}"
        if max_block is not None and block_size > max_block:
            d_hint = f"F max {max_block}"
        elif cutoff is not None and cutoff >= 0 and cutoff > max_cutoff:
            d_hint += ": ora non valido"
    else:
        d_hint = "Inserisci F"

    return f_hint, d_hint


def _parse_int(text: str) -> int | None:
    try:
        return int(text)
    except ValueError:
        return None


def main() -> None:
    root = tk.Tk()
    CompressionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
